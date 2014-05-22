# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from .compat import text_
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.relationships import RelationshipProperty

from . import InvalidStatus

def isoformat(ob):
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
convert_function_dict = {'string': maybe_wrap(text_),
                         'time': maybe_wrap(isoformat),
                         'number': maybe_wrap(float),
                         'integer': maybe_wrap(int),
                         'boolean': maybe_wrap(bool),
                         'date-time': maybe_wrap(isoformat),
                         'date': maybe_wrap(isoformat),
                         'xxx': raise_error}


def converted_of(ob, name, type_):
    try:
        convert_fn = convert_function_dict[type_]
        return convert_fn(getattr(ob, name))
    except KeyError:
        raise Exception("convert {} failure. unknown format {} of {}".format(name, type_, ob))


def attribute_of(ob, name, type_):
    return getattr(ob, name)


def dictify(ob, schema, getter=attribute_of):
    return dictify_properties(ob, schema["properties"], getter=getter)


def jsonify(ob, schema, getter=converted_of):
    return dictify_properties(ob, schema["properties"], getter=getter)


def dictify_properties(ob, properties, getter):
    D = {}
    for k, v in properties.items():
        D[k] = _dictify(ob, k, v, getter)
    return D


def _dictify(ob, name, schema, getter):
    type_ = schema["type"]
    if type_ == "array":
        return [dictify_properties(e, schema["items"], getter) for e in getattr(ob, name)]
    elif type_ == "object":
        return dictify_properties(getattr(ob, name), schema["properties"], getter)
    else:
        return getter(ob, name, type_)


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
        return [_objectify(e, schema["items"], modellookup) for e in params[name]]
    elif type_ is None:  # object
        submodel = modellookup(name)
        result = submodel(**{k: _objectify(params[name], k, schema[k], modellookup) for k in schema})
        modellookup.pop()
        return result
    else:
        return params.get(name)
