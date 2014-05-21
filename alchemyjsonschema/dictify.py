# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from .compat import text_


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
