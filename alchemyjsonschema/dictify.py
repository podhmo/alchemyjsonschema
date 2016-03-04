# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from .compat import text_, long
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
                ('integer', 'int64'): maybe_wrap(long),  # this isn't precisely enough...
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


def attribute_of(ob, name, type_, registry=None):
    return getattr(ob, name)


class DictWalker(object):
    def __init__(self, schema, convert, getter, registry=prepare_dict, marker=marker):
        self.schema = schema
        self.convert = convert
        self.getter = getter
        self.registry = registry
        self.marker = marker

    def __call__(self, ob):
        return self.fold_properties(ob, self.get_properties(self.schema))

    def fold_properties(self, ob, properties):
        if ob is None:
            return None
        D = {}
        for k, v in properties.items():
            val = self.on_property(ob, k, v)
            if val is not self.marker:
                D[k] = val
        return D

    def on_property(self, ob, name, schema):
        type_ = schema.get("type")
        if type_ == "array":
            properties = self.get_properties(schema)
            return [self.fold_properties(e, properties) for e in self.getter(ob, name, [])]
        elif type_ is None:
            return self.fold_properties(self.getter(ob, name), self.get_properties(schema))
        elif type_ == "object":
            return self.fold_properties(self.getter(ob, name), self.get_properties(schema))
        else:
            return self.convert(ob, name, (type_, schema.get("format")), self.registry)

    def get_properties(self, schema):
        return get_properties(schema, self.schema)


def get_reference(schema, root_schema):
    ref = schema["$ref"]
    if not ref.startswith("#/"):
        raise NotImplemented(ref)
    target = root_schema
    for k in ref.split("/")[1:]:
        target = target[k]
    return target


def get_properties(schema, root_schema):
    if "properties" in schema:
        return schema["properties"]
    if "items" in schema:
        return get_properties(schema["items"], root_schema)
    elif "$ref" in schema:
        return get_properties(get_reference(schema, root_schema), root_schema)
    else:
        return schema


def dictify(ob, schema, convert=attribute_of):
    return DictWalker(schema, convert, getattr)(ob)


def jsonify(ob, schema, convert=jsonify_of, registry=jsonify_dict, verbose=False):
    # if verbose option is True, response has None value attributes.
    _marker = marker if verbose else None
    return DictWalker(schema, convert, getattr, registry=registry, marker=_marker)(ob)


def normalize(ob, schema, convert=normalize_of, registry=normalize_dict):
    return DictWalker(schema, convert, dict.get, registry=registry)(ob)


def prepare(ob, schema, convert=prepare_of, registry=prepare_dict):
    return DictWalker(schema, convert, dict.get, registry=registry)(ob)


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
class CreateObjectWalker(object):
    def __init__(self, schema, modellookup, strict=True):
        self.schema = schema
        self.modellookup = modellookup
        self.strict = strict

    def __call__(self, params):
        schema = self.schema
        result = self._create_subobject(params, schema["title"], schema)
        assert self.modellookup.name_stack == []
        return result

    def fold_properties(self, params, properties):
        D = {}
        for k, schema in properties.items():
            D[k] = self.on_property(params, k, schema)
        return D

    def on_property(self, params, name, schema):
        type_ = schema.get("type")
        if params is None:
            return [] if type_ == "array" else None  # xxx

        if type_ == "array":
            sub_schema = self.get_properties(schema)
            return [self._create_subobject(e, name, sub_schema) for e in params.get(name, [])]
        elif name not in params:
            return None
        elif type_ == "object":
            sub_params = params[name]
            return self._create_subobject(sub_params, name, schema)
        elif type_ is None:  # object
            sub_params = params.get(name)
            if sub_params is None:
                return None
            return self._create_subobject(sub_params, name, schema)
        else:
            return params.get(name)

    def _create_subobject(self, params, name, schema):
        sub_model = self.modellookup(name)
        sub_params = self.fold_properties(params, self.get_properties(schema))
        sub = sub_model(**sub_params)
        self.modellookup.pop()
        if self.strict:
            for k in schema.get("required", []):
                if getattr(sub, k) is None:
                    raise InvalidStatus("{}.{} is None. this is required.".format(sub_model, k))
        return sub

    def get_properties(self, schema):
        return get_properties(schema, self.schema)


def objectify(params, schema, modellookup, strict=True):
    return CreateObjectWalker(schema, modellookup, strict)(params)


# apply_changes
def apply_changes(ob, params, schema, modellookup):
    return UpdateObjectWalker(schema, modellookup)(ob, params)


class UpdateObjectWalker(object):
    def __init__(self, schema, modellookup, strict=True):
        self.schema = schema
        self.modellookup = modellookup
        self.strict = strict
        self.create_walker = CreateObjectWalker(schema, modellookup, strict)

    def __call__(self, ob, params):
        schema = self.schema
        model_class = self.modellookup(schema["title"])
        params = self.fold_properties(ob, params, self.get_properties(schema))
        assert model_class == ob.__class__
        self.modellookup.pop()
        assert self.modellookup.name_stack == []
        return ob

    def get_properties(self, schema):
        return get_properties(schema, self.schema)

    def fold_properties(self, ob, params, properties):
        for k, schema in properties.items():
            setattr(ob, k, self.on_property(ob, params, k, schema))
        return ob

    def on_property(self, ob, params, name, schema):
        type_ = schema.get("type")
        if params is None:
            return [] if type_ == "array" else None  # xxx

        if type_ == "array":
            sub_schema = self.get_properties(schema)
            access = getattr(ob, name)
            for ac, sub, sub_params in list(subobject_iterate(ob, params, name)):
                if ac == "create":
                    access.append(self.create_walker._create_subobject(sub_params, name, sub_schema))
                elif ac == "update":
                    for k, v in sub_params.items():  # xxx:
                        setattr(sub, k, v)
                elif ac == "delete":
                    access.remove(sub)
            return getattr(ob, name)
        elif name not in params:
            return None
        elif type_ == "object":
            sub_params = params[name]
            return self._update_subobject(ob, sub_params, name, schema)
        elif type_ is None:  # object
            sub_params = params.get(name)
            if sub_params is None:
                return None
            return self._update_subobject(ob, sub_params, name, schema)
        else:
            return params.get(name)

    def _update_subobject(self, parent, params, name, schema):
        if params is None:
            return None
        sub = getattr(parent, name, None)
        if sub is None:
            return self.create_walker._create_subobject(params, name, schema)
        else:
            sub_model = self.modellookup(name)
            assert sub.__class__ == sub_model
            sub = self.fold_properties(sub, params, self.get_properties(schema))
            self.modellookup.pop()
            return sub


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


def _get_primary_keys_from_object(ob):
    return tuple(sorted(col.name for col in inspect(ob).mapper.primary_key))


def _get_primary_keys_from_params(sub_params, primary_keys):
    return tuple(sorted(sub_params.get(k) for k in primary_keys))


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
