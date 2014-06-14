# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from .compat import text_
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.relationships import RelationshipProperty
from functools import partial
import isodate
from .custom.format import (
    parse_time,  # more strict than isodate
    parse_date   # more strict
)
from collections import OrderedDict
from jsonschema import validate
from . import InvalidStatus
import pytz


class ConvertionError(Exception):
    def __init__(self, name, message):
        self.name = name
        self.message = message


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

prepare_dict = {'string': maybe_wrap(text_),
                'number': maybe_wrap(float),
                'integer': maybe_wrap(int),
                'boolean': maybe_wrap(bool)}


def jsonify_of(ob, name, type_, registry=jsonify_dict):
    try:
        convert_fn = registry[type_]
    except KeyError:
        raise ConvertionError(name, "convert {} failure. unknown format {} of {}".format(name, type_, ob))
    return convert_fn(getattr(ob, name, None))

marker = object()


def normalize_of(ob, name, type_, registry=normalize_dict):
    try:
        convert_fn = registry[type_]
    except KeyError:
        raise ConvertionError(name, "convert {} failure. unknown format {} of {}".format(name, type_, ob))
    try:
        val = ob.get(name, marker)
        if val is marker:
            return val
        return convert_fn(val)
    except ValueError as e:
        raise ConvertionError(name, e.args[0])


def prepare_of(ob, name, type_, registry=prepare_dict):
    val = ob.get(name, marker)
    if val is marker:
        return val
    try:
        convert_fn = registry[type_[0]]
        return convert_fn(val)
    except KeyError:
        return val
    except ValueError as e:
        raise ConvertionError(name, e.args[0])


def attribute_of(ob, name, type_):
    return getattr(ob, name)


def dictify(ob, schema, convert=attribute_of, getter=getattr):
    return dictify_properties(ob, schema["properties"], convert=convert, getter=getter)


def jsonify(ob, schema, convert=jsonify_of, getter=getattr, registry=jsonify_dict):
    convert = partial(convert, registry=registry)
    return dictify_properties(ob, schema["properties"], convert=convert, getter=getter)


def normalize(ob, schema, convert=normalize_of, getter=dict.get, registry=normalize_dict):
    convert = partial(convert, registry=registry)
    return dictify_properties(ob, schema["properties"], convert=convert, getter=getter)


def prepare(ob, schema, convert=prepare_of, getter=dict.get, registry=prepare_dict):
    convert = partial(convert, registry=registry)
    return dictify_properties(ob, schema["properties"], convert=convert, getter=getter)


def dictify_properties(ob, properties, convert, getter, marker=marker):
    if ob is None:
        return None
    D = {}
    for k, v in properties.items():
        val = _dictify(ob, k, v, convert, getter)
        if val is not marker:
            D[k] = val
    return D


def _dictify(ob, name, schema, convert, getter):
    type_ = schema.get("type")
    if type_ == "array":
        return [dictify_properties(e, schema["items"], convert, getter) for e in getter(ob, name, [])]
    elif type_ is None:
        return dictify_properties(getter(ob, name), schema, convert, getter)
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
def _objectify_subobject(params, name, schema, modellookup):
    sub_model = modellookup(name)
    sub_params = objectify_propperties(params, schema, modellookup)
    sub = sub_model(**sub_params)
    modellookup.pop()
    return sub


def objectify(params, schema, modellookup, strict=True):
    model_class = modellookup(schema["title"])
    params = objectify_propperties(params, schema["properties"], modellookup)
    result = model_class(**params)
    modellookup.pop()
    if strict:
        for k in schema.get("required", []):
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
    if params is None:
        return [] if type_ == "array" else None  # xxx

    if type_ == "array":
        sub_schema = schema["items"]
        return [_objectify_subobject(e, name, sub_schema, modellookup) for e in params.get(name, [])]
    elif name not in params:
        return None
    elif type_ is None:  # object
        sub_params = params.get(name)
        if sub_params is None:
            return None
        return _objectify_subobject(params[name], name, schema, modellookup)
    else:
        return params.get(name)


# apply_changes
def _apply_changes_subobject(parent, params, name, schema, modellookup):
    if params is None:
        return None
    sub = getattr(parent, name, None)
    if sub is None:
        return _objectify_subobject(params, name, schema, modellookup)
    else:
        sub_model = modellookup(name)
        assert sub.__class__ == sub_model
        sub = apply_changes_propperties(sub, params, schema, modellookup)
        modellookup.pop()
        return sub


def apply_changes(ob, params, schema, modellookup):
    model_class = modellookup(schema["title"])
    params = apply_changes_propperties(ob, params, schema["properties"], modellookup)
    assert model_class == ob.__class__
    modellookup.pop()
    assert modellookup.name_stack == []
    return ob


def apply_changes_propperties(ob, params, properties, modellookup):
    for k, schema in properties.items():
        setattr(ob, k, _apply_changes(ob, params, k, schema, modellookup))
    return ob


def _get_primary_keys_from_object(ob):
    return tuple(sorted(col.name for col in inspect(ob).mapper.primary_key))


def _get_primary_keys_from_params(sub_params, primary_keys):
    return tuple(sorted(sub_params.get(k) for k in primary_keys))


def subobject_iterate(ob, params, name):
    cache = OrderedDict()
    used_children = set()

    primary_keys = None

    for sub in getattr(ob, name):
        if primary_keys is None:
            primary_keys = _get_primary_keys_from_object(ob)
        cache[primary_keys] = sub

    for sub_params in params.get(name, []):
        keys = _get_primary_keys_from_params(sub_params, primary_keys)
        if keys in cache:
            sub = cache[keys]
            yield "update", sub, sub_params
            used_children.add(sub)
        else:
            yield "create", None, sub_params

    for sub in getattr(ob, name):
        if sub not in used_children:
            yield "delete", sub, None


def _apply_changes(ob, params, name, schema, modellookup):
    type_ = schema.get("type")
    if params is None:
        return [] if type_ == "array" else None  # xxx

    if type_ == "array":
        sub_schema = schema["items"]
        access = getattr(ob, name)
        for ac, sub, sub_params in list(subobject_iterate(ob, params, name)):
            if ac == "create":
                access.append(_objectify_subobject(sub_params, name, sub_schema, modellookup))
            elif ac == "update":
                for k, v in sub_params.items():  # xxx:
                    setattr(sub, k, v)
            elif ac == "delete":
                access.remove(sub)
        return getattr(ob, name)
    elif name not in params:
        return None
    elif type_ is None:  # object
        sub_params = params.get(name)
        if sub_params is None:
            return None
        return _apply_changes_subobject(ob, params[name], name, schema, modellookup)
    else:
        return params.get(name)


class ErrorFound(Exception):  # xxx:
    def __init__(self, errors):
        self.errors = errors


def raise_error(data, e):
    raise e


def validate_all(data, validator, treat_error=raise_error):
    errors = []
    for e in validator.iter_errors(data):
        errors.append(e)
    if errors:
        return treat_error(data, ErrorFound(errors))
    return data
