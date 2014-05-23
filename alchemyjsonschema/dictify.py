# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from operator import getitem
from .compat import text_
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.relationships import RelationshipProperty
import isodate
from .custom.format import (
    parse_time,  # more strict than isodate
    parse_date   # more strict
)
from . import InvalidStatus
import pytz


def datetime_rfc3339(ob):
    if ob.tzinfo:
        return ob.isoformat()
    return pytz.utc.localize(ob).isoformat()


def isoformat(ob):
    return ob.isoformat() + "Z"  # xxx


def isoformat0(ob):
    return ob.isoformat()


def raise_error(ob):
    raise Exception("convert failure. unknown format xxx of {}".format(ob))


def maybe_wrap(fn, default=None):
    def wrapper(ob):
        if ob is None:
            return default
        return fn(ob)
    return wrapper

# todo: look at required or not
jsonify_dict = {('string', None): maybe_wrap(text_),
                ('string', 'time',): maybe_wrap(isoformat),
                ('number', None): maybe_wrap(float),
                ('integer', None): maybe_wrap(int),
                ('boolean', None): maybe_wrap(bool),
                ('string', 'date-time'): maybe_wrap(datetime_rfc3339),
                ('string', 'date'): maybe_wrap(isoformat0),
                ('xxx', None): raise_error}


normalize_dict = {('string', None): maybe_wrap(text_),
                  ('string', 'time',): maybe_wrap(parse_time),
                  ('number', None): maybe_wrap(float),
                  ('integer', None): maybe_wrap(int),
                  ('boolean', None): maybe_wrap(bool),
                  ('string', 'date-time'): maybe_wrap(isodate.parse_datetime),
                  ('string', 'date'): maybe_wrap(parse_date),
                  ('xxx', None): raise_error}


def jsonify_of(ob, name, type_):
    try:
        convert_fn = jsonify_dict[type_]
        return convert_fn(getattr(ob, name))
    except KeyError:
        raise Exception("convert {} failure. unknown format {} of {}".format(name, type_, ob))


def normalize_of(ob, name, type_):
    try:
        convert_fn = normalize_dict[type_]
        return convert_fn(ob[name])
    except KeyError:
        raise Exception("convert {} failure. unknown format {} of {}".format(name, type_, ob))


def attribute_of(ob, name, type_):
    return getattr(ob, name)


def dictify(ob, schema, convert=attribute_of, getter=getattr):
    return dictify_properties(ob, schema["properties"], convert=convert, getter=getter)


def jsonify(ob, schema, convert=jsonify_of, getter=getattr):
    return dictify_properties(ob, schema["properties"], convert=convert, getter=getter)


def normalize(ob, schema, convert=normalize_of, getter=getitem):
    return dictify_properties(ob, schema["properties"], convert=convert, getter=getter)


def dictify_properties(ob, properties, convert, getter):
    D = {}
    for k, v in properties.items():
        D[k] = _dictify(ob, k, v, convert, getter)
    return D


def _dictify(ob, name, schema, convert, getter):
    type_ = schema["type"]
    if type_ == "array":
        return [dictify_properties(e, schema["items"], convert, getter) for e in getter(ob, name)]
    elif type_ == "object":
        return dictify_properties(getter(ob, name), schema["properties"], convert, getter)
    else:
        return convert(ob, name, (type_, schema.get("format")))


class ModelLookup(object):
    def __init__(self, module):
        self.module = module
        self.name_stack = []
        self.inspect_stack = []

    def __call__(self, name):
        if not self.name_stack:
            self.name_stack.append(name)
            model = getattr(self.module, name)
            self.inspect_stack.append(inspect(model))
            return model
        else:
            self.name_stack.append(name)
            prop = self.inspect_stack[-1].get_property(name)
            assert isinstance(prop, RelationshipProperty)
            mapper = prop.mapper
            model = mapper.class_
            self.inspect_stack.append(mapper)
            return model

    def pop(self):
        name = self.name_stack.pop()
        return name, self.inspect_stack.pop()


class ComposedModule(object):
    def __init__(self, *modules):
        self.modules = set(modules)

    def __getattr__(self, k):
        for m in self.modules:
            if hasattr(m, k):
                return getattr(m, k)


# objectify
def objectify(params, schema, modellookup, strict=True):
    model_class = modellookup(schema["title"])
    result = model_class(**objectify_propperties(params, schema["properties"], modellookup))
    modellookup.pop()
    if strict:
        for k in schema["required"]:
            if getattr(result, k) is None:
                raise InvalidStatus("{}.{} is None. this is required.".format(model_class, k))
    assert modellookup.name_stack == []
    return result


def objectify_propperties(params, properties, modellookup):
    D = {}
    for k, schema in properties.items():
        D[k] = _objectify(params, k, schema, modellookup)
    return D


def _objectify(params, name, schema, modellookup):
    type_ = schema.get("type")
    if type_ == "array":
        return [_objectify_subobject(e, name, schema["items"], modellookup) for e in params[name]]
    elif type_ is None:  # object
        submodel = modellookup(name)
        result = submodel(**{k: _objectify(params[name], k, schema[k], modellookup) for k in schema})
        modellookup.pop()
        return result
    else:
        return params.get(name)


def _objectify_subobject(params, name, schema, modellookup):
    submodel = modellookup(name)
    result = submodel(**{k: _objectify(params, k, v, modellookup) for k, v in schema.items()})
    modellookup.pop()
    return result
