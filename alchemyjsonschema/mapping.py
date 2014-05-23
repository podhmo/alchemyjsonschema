# -*- coding:utf-8 -*-
from functools import partial
from .dictify import (
    objectify,
    jsonify,
    dictify,
    normalize,
    ModelLookup
)
from jsonschema import (
    validate,
    FormatChecker
)
from jsonschema.validators import (
    Draft3Validator,
    Draft4Validator
)


class Mapping(object):
    def __init__(self, validator, model, modellookup):
        self.validator = validator
        self.format_checker = validator.format_checker
        self.schema = validator.schema
        self.model = model
        self.modellookup = modellookup

    def jsondict_from_object(self, ob):
        return jsonify(ob, self.schema)

    def dict_from_jsondict(self, jsondict):
        return normalize(jsondict, self.schema)

    def dict_from_object(self, ob):
        return dictify(ob, self.schema)

    def object_from_dict(self, params, strict=True):
        return objectify(params, self.schema, self.modellookup, strict=strict)

    def validate_jsondict(self, jsondict):
        return validate(jsondict, self.schema, format_checker=self.format_checker)

    def validate_all_jsondict(self, jsondict):
        return validate_all(jsondict, self.validator)


class ErrorFound(Exception):  # xxx:
    pass


def validate_all(data, validator):
    errors = []
    for e in validator.iter_errors(data):
        errors.append(dict(name=e.path[0], reason=e.validator))
    if errors:
        raise ErrorFound(errors)
    return None


class MappingFactory(object):
    _Mapping = Mapping
    _ModelLookup = ModelLookup

    def __init__(self, validator_class, schema_factory, module, resolver=None, format_checker=None):
        self.schema_factory = schema_factory
        self.validator_class = validator_class
        self.resolver = resolver
        self.format_checker = format_checker or FormatChecker()
        self.module = module

    def create(self, model, includes=None, excludes=None, depth=None):
        schema = self.schema_factory.create(model, includes=includes, excludes=excludes, depth=depth)
        validator = self.validator_class(schema, resolver=self.resolver, format_checker=self.format_checker)
        modellookup = self._ModelLookup(self.module)
        mapping = self._Mapping(validator, model, modellookup)
        return mapping

Draft3MappingFactory = partial(MappingFactory, Draft3Validator)
Draft4MappingFactory = partial(MappingFactory, Draft4Validator)
