# -*- coding:utf-8 -*-
import logging
from collections import OrderedDict
import sqlalchemy.types as t
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.visitors import VisitableType
from sqlalchemy.orm.base import ONETOMANY, MANYTOONE, MANYTOMANY
from sqlalchemy.sql.type_api import TypeEngine
logger = logging.getLogger(__name__)

EMPTY_DICT = {}


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
default_column_to_schema = {
    t.String: "string",
    t.Text: "string",
    t.Integer: "integer",
    t.SmallInteger: "integer",
    t.BigInteger: "string",  # xxx
    t.Numeric: "integer",
    t.Float: "number",
    t.DateTime: "string",
    t.Date: "string",
    t.Time: "string",  # xxx
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
    if column.type.length is not None:
        sub["maxLength"] = column.type.length


def enum_one_of(column, sub):
    sub["enum"] = list(column.type.enums)


def datetime_format(column, sub):
    sub["format"] = "date-time"


def date_format(column, sub):
    sub["format"] = "date"


def time_format(column, sub):
    sub["format"] = "time"


default_restriction_dict = {
    t.String: string_max_length,
    t.Enum: enum_one_of,
    t.DateTime: datetime_format,
    t.Date: date_format,
    t.Time: time_format
}


class Classifier(object):
    def __init__(self, mapping=default_column_to_schema, see_mro=True, see_impl=True):
        self.mapping = mapping
        self.see_mro = see_mro
        self.see_impl = see_impl

    def __getitem__(self, k):
        cls = k.__class__
        _, mapped = get_class_mapping(self.mapping, cls, see_mro=self.see_mro, see_impl=self.see_impl)
        if mapped is None:
            raise InvalidStatus("notfound: {k}. (cls={cls})".format(k=k, cls=cls))
        return cls, mapped


def get_class_mapping(mapping, cls, see_mro=True, see_impl=True):
    v = mapping.get(cls)
    if v is not None:
        return cls, v

    # inheritance
    if see_mro:
        for type_ in cls.mro()[1:]:
            if type_ is TypeEngine:
                break
            if type_ in mapping:
                return type_, mapping[type_]

    # type decorator
    if see_impl and hasattr(cls, "impl"):
        impl = cls.impl
        if not callable(impl):
            # If the class level impl is not a callable (the unusual case),
            impl = impl.__class__
        return get_class_mapping(mapping, impl, see_mro=see_mro, see_impl=see_impl)
    return None, None


DefaultClassfier = Classifier(default_column_to_schema)
Empty = ()


class BaseModelWalker(object):
    def __init__(self, model, includes=None, excludes=None, history=None):
        self.mapper = inspect(model).mapper
        self.includes = includes
        self.excludes = excludes
        self.history = history or []
        if includes and excludes:
            if set(includes).intersection(excludes):
                raise InvalidStatus("Conflict includes={}, exclude={}".format(includes, excludes))

    def clone(self, name, mapper, includes, excludes, history):
        return self.__class__(mapper, includes, excludes, history)

    def from_child(self, model):
        return self.__class__(model, history=self.history)

# mapper.column_attrs and mapper.attrs is not ordered. define our custom iterate function `iterate'


class ForeignKeyWalker(BaseModelWalker):
    def iterate(self):
        for c in self.mapper.local_table.columns:
            yield self.mapper._props[c.name]  # danger!! not immutable

    def walk(self):
        for prop in self.iterate():
            if self.includes is None or prop.key in self.includes:
                if self.excludes is None or prop.key not in self.excludes:
                    yield prop


class NoForeignKeyWalker(BaseModelWalker):
    def iterate(self):
        for c in self.mapper.local_table.columns:
            yield self.mapper._props[c.name]  # danger!! not immutable

    def walk(self):
        for prop in self.iterate():
            if self.includes is None or prop.key in self.includes:
                if self.excludes is None or prop.key not in self.excludes:
                    if not any(c.foreign_keys for c in getattr(prop, "columns", Empty)):
                        yield prop


class StructuralWalker(BaseModelWalker):
    def iterate(self):
        # self.mapper.attrs
        for c in self.mapper.local_table.columns:
            yield self.mapper._props[c.name]  # danger!! not immutable
        for prop in self.mapper.relationships:
            yield prop

    def walk(self):
        for prop in self.iterate():
            if isinstance(prop, (ColumnProperty, RelationshipProperty)):
                if self.includes is None or prop.key in self.includes:
                    if self.excludes is None or prop.key not in self.excludes:
                        if prop not in self.history:
                            if not any(c.foreign_keys for c in getattr(prop, "columns", Empty)):
                                yield prop


def get_children(name, params, splitter=".", default=None):  # todo: rename
    prefix = name + splitter
    if hasattr(params, "items"):
        return {k.split(splitter, 1)[1]: v for k, v in params.items() if k.startswith(prefix)}
    elif isinstance(params, (list, tuple)):
        return [e.split(splitter, 1)[1] for e in params if e.startswith(prefix)]
    else:
        return default


pop_marker = object()


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
    def __init__(self, splitter=".", bidirectional=False):
        self.splitter = splitter
        self.bidirectional = bidirectional

    def default_excludes(self, prop):
        return [prop.back_populates, prop.backref]

    def child_overrides(self, prop, overrides):
        name = prop.key
        children = get_children(name, overrides.params, splitter=self.splitter)
        return overrides.__class__(children, pop_marker=overrides.pop_marker)

    def child_walker(self, prop, walker, history=None):
        name = prop.key
        excludes = get_children(name, walker.includes, splitter=self.splitter, default=[])
        if not self.bidirectional:
            excludes.extend(self.default_excludes(prop))
        includes = get_children(name, walker.includes, splitter=self.splitter)

        return walker.clone(name, prop.mapper, includes=includes, excludes=excludes, history=history)

    def child_schema(self, prop, schema_factory, root_schema, walker, overrides, depth, history):
        subschema = schema_factory._build_properties(walker, root_schema, overrides, depth=(depth and depth - 1), history=history, toplevel=False)
        if prop.direction == ONETOMANY:
            return {"type": "array", "items": subschema}
        else:
            return {"type": "object", "properties": subschema}

RELATIONSHIP = "relationship"
FOREIGNKEY = "foreignkey"
IMMEDIATE = "immediate"


class RelationDesicion(object):
    def desicion(self, walker, prop, toplevel):
        if hasattr(prop, "mapper"):
            yield RELATIONSHIP, prop, EMPTY_DICT
        elif hasattr(prop, "columns"):
            yield FOREIGNKEY, prop, EMPTY_DICT
        else:
            raise NotImplemented(prop)


class UseForeignKeyIfPossibleDecision(object):
    def desicion(self, walker, prop, toplevel):
        if hasattr(prop, "mapper"):
            if prop.direction == MANYTOONE:
                if toplevel:
                    for c in prop.local_columns:
                        yield FOREIGNKEY, walker.mapper._props[c.name], {"relation": prop.key}
                else:
                    rp = walker.history[0]
                    if prop.local_columns != rp.remote_side:
                        for c in prop.local_columns:
                            yield FOREIGNKEY, walker.mapper._props[c.name], {"relation": prop.key}
            elif prop.direction == MANYTOMANY:
                # logger.warn("skip mapper=%s, prop=%s is many to many.", walker.mapper, prop)
                yield {"type": "array", "items": {"type": "string"}}, prop, EMPTY_DICT
            else:
                yield RELATIONSHIP, prop, EMPTY_DICT
        elif hasattr(prop, "columns"):
            yield FOREIGNKEY, prop, EMPTY_DICT
        else:
            raise NotImplemented(prop)


class SchemaFactory(object):
    def __init__(self, walker,
                 classifier=DefaultClassfier,
                 restriction_dict=default_restriction_dict,
                 container_factory=OrderedDict,
                 child_factory=ChildFactory("."),
                 relation_decision=RelationDesicion()):
        self.container_factory = container_factory
        self.classifier = classifier
        self.walker = walker  # class
        self.restriction_set = [{k: v} for k, v in restriction_dict.items()]
        self.child_factory = child_factory
        self.relation_decision = relation_decision

    def __call__(self, model, includes=None, excludes=None, overrides=None, depth=None):
        walker = self.walker(model, includes=includes, excludes=excludes)
        overrides = CollectionForOverrides(overrides or {})

        schema = {
            "title": model.__name__,
            "type": "object",
        }
        schema["properties"] = self._build_properties(walker, schema, overrides=overrides, depth=depth)

        if overrides.not_used_keys:
            raise InvalidStatus("invalid overrides: {}".format(overrides.not_used_keys))

        if model.__doc__:
            schema["description"] = model.__doc__

        required = self._detect_required(walker)

        if required:
            schema["required"] = required
        return schema

    def _add_restriction_if_found(self, D, column, itype):
        for restriction_dict in self.restriction_set:
            _, fn = get_class_mapping(restriction_dict, itype, see_impl=self.classifier.see_impl, see_mro=self.classifier.see_mro)
            if fn is not None:
                if isinstance(fn, (list, tuple)):
                    for f in fn:
                        f(column, D)
                else:
                    fn(column, D)

    def _add_property_with_reference(self, walker, root_schema, current_schema, prop, val):
        clsname = prop.mapper.class_.__name__
        if "definitions" not in root_schema:
            root_schema["definitions"] = {}

        if val["type"] == "object":
            current_schema[prop.key] = {"$ref": "#/definitions/{}".format(clsname)}
            val["required"] = self._detect_required(walker.from_child(prop.mapper))
            root_schema["definitions"][clsname] = val
        else:  # array
            current_schema[prop.key] = {"type": "array", "items": {"$ref": "#/definitions/{}".format(clsname)}}
            val["type"] = "object"
            val["properties"] = val.pop("items")
            val["required"] = self._detect_required(walker.from_child(prop.mapper))
            root_schema["definitions"][clsname] = val

    def _build_properties(self, walker, root_schema, overrides, depth=None, history=None, toplevel=True):
        if depth is not None and depth <= 0:
            return self.container_factory()

        D = self.container_factory()
        if history is None:
            history = []

        for prop in walker.walk():
            for action, prop, opts in self.relation_decision.desicion(walker, prop, toplevel):
                if action == RELATIONSHIP:     # RelationshipProperty
                    history.append(prop)
                    subwalker = self.child_factory.child_walker(prop, walker, history=history)
                    suboverrides = self.child_factory.child_overrides(prop, overrides)
                    value = self.child_factory.child_schema(prop, self, root_schema, subwalker, suboverrides, depth=depth, history=history)
                    self._add_property_with_reference(walker, root_schema, D, prop, value)
                    history.pop()
                elif action == FOREIGNKEY:  # ColumnProperty
                    for c in prop.columns:
                        sub = {}
                        if type(c.type) != VisitableType:
                            itype, sub["type"] = self.classifier[c.type]

                            self._add_restriction_if_found(sub, c, itype)

                            if c.doc:
                                sub["description"] = c.doc

                            if c.name in overrides:
                                overrides.overrides(sub)
                            if opts:
                                sub.update(opts)
                            D[c.name] = sub
                        else:
                            raise NotImplemented
                    D[prop.key] = sub
                else:  # immediate
                    D[prop.key] = action
        return D

    def _detect_required(self, walker):
        r = []
        for prop in walker.walk():
            columns = getattr(prop, "columns", Empty)
            if any(not c.nullable and c.default is None for c in columns):
                r.append(prop.key)
        return r
