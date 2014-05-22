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
    t.BigInteger: "integer",  # xxx
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


def get_children(name, params, splitter=".", default=None):  # todo: rename
    prefix = name + splitter
    if hasattr(params, "items"):
        return {k.split(splitter, 1)[0]: v for k, v in params.items() if k.startswith(prefix)}
    elif isinstance(params, (list, tuple)):
        return [e.split(splitter, 1)[0] for e in params if e.startswith(prefix)]
    else:
        return default


class CollectionForOverrides(object):
    def __init__(self, params, pop_marker=pop_marker):
        self.params = params or {}
        self.not_used_keys = set(params.keys())
        self.pop_marker = pop_marker

    def __contains__(self, k):
        return k in self.params

    def overrides(self, basedict):
        for k, v in self.params.items():
            if v == self.pop_marker:
                basedict.pop(k)  # xxx: KeyError?
            else:
                basedict[k] = v
            self.not_used_keys.remove(k)  # xxx: KeyError?


class ChildFactory(object):
    def __init__(self, splitter="."):
        self.splitter = splitter

    def default_excludes(self, prop):
        return [prop.back_populates, prop.backref]

    def child_overrides(self, prop, overrides):
        name = prop.key
        children = get_children(name, overrides.params, splitter=self.splitter)
        return overrides.__class__(children, pop_marker=overrides.pop_marker)

    def child_walker(self, prop, walker):
        name = prop.key
        excludes = get_children(name, walker.includes, splitter=self.splitter, default=[])
        excludes.extend(self.default_excludes(prop))

        includes = get_children(name, walker.includes, splitter=self.splitter)

        return walker.__class__(prop.mapper, includes=includes, excludes=excludes)

    def child_schema(self, prop, schema_factory, walker, overrides, depth):
        subschema = schema_factory._build_properties(walker, overrides, depth=(depth and depth - 1))
        if prop.direction == ONETOMANY:
            return {"type": "array", "items": subschema}
        else:
            return subschema


class SchemaFactory(object):
    def __init__(self, walker,
                 classifier=DefaultClassfier,
                 restriction_dict=default_restriction_dict,
                 child_factory=ChildFactory(".")):
        self.classifier = classifier
        self.walker = walker  # class
        self.restriction_dict = restriction_dict
        self.child_factory = child_factory

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
                subwalker = self.child_factory.child_walker(prop, walker)
                suboverrides = self.child_factory.child_overrides(prop, overrides)
                D[prop.key] = self.child_factory.child_schema(prop, self, subwalker, suboverrides, depth=depth)
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
