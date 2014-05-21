# -*- coding:utf-8 -*-
import sqlalchemy.types as t
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.visitors import VisitableType
from sqlalchemy.orm.base import ONETOMANY

class InvalidStatus(Exception):
    pass

"""
http://json-schema.org/latest/json-schema-core.html#anchor8
3.5.  JSON Schema primitive types

JSON Schema defines seven primitive types for JSON values:

    array
        A JSON array.
    boolean
        A JSON boolean.
    integer
        A JSON number without a fraction or exponent part.
    number
        Any JSON number. Number includes integer.
    null
        The JSON null value.
    object
        A JSON object.
    string
        A JSON string.
"""

#  tentative
default_mapping = {
    t.String: "string",
    t.Text: "string",
    t.Integer: "integer",
    t.SmallInteger: "integer",
    t.BigInteger: "integer",
    t.Numeric: "integer",
    t.Float: "number",
    t.DateTime: "date-time",
    t.Date: "date",
    t.Time: "time",
    t.LargeBinary: "xxx",
    t.Binary: "xxx",
    t.Boolean: "boolean",
    t.Unicode: "string",
    t.Concatenable: "xxx",
    t.UnicodeText: "string",
    t.Interval: "xxx",
    t.Enum: "string",
}


# restriction
def string_max_length(column, sub):
    sub["maxLength"] = column.type.length


def enum_one_of(column, sub):
    sub["enum"] = list(column.type.enums)

default_restriction_dict = {
    t.String: string_max_length,
    t.Enum: enum_one_of
}


class Classifier(object):
    def __init__(self, mapping=default_mapping):
        self.mapping = mapping

    def __getitem__(self, k):
        cls = k.__class__
        v = self.mapping.get(cls)
        if v is not None:
            return cls, v
        # inheritance
        for type_ in self.mapping:
            if issubclass(cls, type_):
                return type_, self.mapping[type_]
        raise InvalidStatus("notfound")

DefaultClassfier = Classifier(default_mapping)
Empty = ()


class BaseModelWalker(object):
    def __init__(self, model, includes=None, excludes=None):
        self.mapper = inspect(model).mapper
        self.includes = includes
        self.excludes = excludes
        if includes and excludes:
            if set(includes).intersection(excludes):
                raise InvalidStatus("Conflict includes={}, exclude={}".format(includes, excludes))


class SingleModelWalker(BaseModelWalker):
    def walk(self):
        for prop in self.mapper.attrs:
            if isinstance(prop, ColumnProperty):
                if self.includes is None or prop.key in self.includes:
                    if self.excludes is None or prop.key not in self.excludes:
                        yield prop


class OneModelOnlyWalker(BaseModelWalker):
    def walk(self):
        for prop in self.mapper.attrs:
            if isinstance(prop, ColumnProperty):
                if self.includes is None or prop.key in self.includes:
                    if self.excludes is None or prop.key not in self.excludes:
                        if not any(c.foreign_keys for c in getattr(prop, "columns", Empty)):
                            yield prop


class AlsoChildrenWalker(BaseModelWalker):
    def walk(self):
        for prop in self.mapper.attrs:
            if isinstance(prop, (ColumnProperty, RelationshipProperty)):
                if self.includes is None or prop.key in self.includes:
                    if self.excludes is None or prop.key not in self.excludes:
                        if not any(c.foreign_keys for c in getattr(prop, "columns", Empty)):
                            yield prop

pop_marker = object()


class CollectionForOverrides(object):
    def __init__(self, params, pop_marker=pop_marker):
        self.params = params or {}
        self.not_used_keys = set(params.keys())
        self.pop_marker = pop_marker

    def __contains__(self, k):
        return k in self.params

    def get_child(self, k):
        return self.__class__(self.params.get(k, {}), pop_marker=self.pop_marker)

    def overrides(self, basedict):
        for k, v in self.params.items():
            if v == self.pop_marker:
                basedict.pop(k)  # xxx: KeyError?
            else:
                basedict[k] = v
            self.not_used_keys.remove(k)  # xxx: KeyError?


class SchemaFactory(object):
    def __init__(self, walker, classifier=DefaultClassfier, restriction_dict=default_restriction_dict):
        self.classifier = classifier
        self.walker = walker  # class
        self.restriction_dict = restriction_dict

    def create(self, model, includes=None, excludes=None, overrides=None, depth=None):
        walker = self.walker(model, includes=includes, excludes=excludes)
        overrides = CollectionForOverrides(overrides or {})

        schema = {
            "title": model.__name__,
            "type": "object",
            "properties": self._build_properties(walker, overrides=overrides, depth=depth)
        }

        if overrides.not_used_keys:
            raise InvalidStatus("invalid overrides: {}".format(overrides.not_used_keys))

        if model.__doc__:
            schema["description"] = model.__doc__

        required = self._detect_required(walker)

        if required:
            schema["required"] = required
        return schema

    def _build_properties(self, walker, overrides, depth=None):
        if depth is not None and depth <= 0:
            return {}

        D = {}
        for prop in walker.walk():
            if hasattr(prop, "mapper"):     # RelationshipProperty
                subwalker = walker.__class__(prop.mapper, excludes=[prop.back_populates, prop.backref])
                suboverrides = overrides.get_child(prop.key)
                subschema = self._build_properties(subwalker, suboverrides, depth=(depth and depth - 1))
                if prop.direction == ONETOMANY:
                    D[prop.key] = {"type": "array", "items": subschema}
                else:
                    D[prop.key] = subschema
            elif hasattr(prop, "columns"):  # ColumnProperty
                for c in prop.columns:
                    sub = {}
                    if type(c.type) != VisitableType:
                        itype, sub["type"] = self.classifier[c.type]
                        for tcls in itype.__mro__:
                            fn = self.restriction_dict.get(tcls)
                            if fn is not None:
                                fn(c, sub)

                        if c.doc:
                            sub["description"] = c.doc

                        if c.name in overrides:
                            overrides.overrides(sub)

                        D[c.name] = sub
                    else:
                        raise NotImplemented
                D[prop.key] = sub
        return D

    def _detect_required(self, walker):
        return [prop.key for prop in walker.walk() if any(not c.nullable for c in getattr(prop, "columns", Empty))]
