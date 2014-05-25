# -*- coding:utf-8 -*-
from functools import partial
from .dictify import (
    objectify,
    jsonify,
    dictify,
    normalize,
    validate_all,
    ModelLookup,
    jsonify_dict,
    normalize_dict,
)
from jsonschema import (
    validate,
    FormatChecker
)
from jsonschema.validators import (
    Draft3Validator,
    Draft4Validator
)
from . import (
    default_restriction_dict,
    default_column_to_schema
)


class DefaultRegistry:
    jsonify = jsonify_dict
    normalize = normalize_dict
    restriction = default_restriction_dict
    column_to_schema = default_column_to_schema


class Mapping(object):
    def __init__(self, validator, model, modellookup, registry=DefaultRegistry):
        self.validator = validator
        self.format_checker = validator.format_checker
        self.schema = validator.schema
        self.model = model
        self.modellookup = modellookup
        self.registry = registry

    def jsondict_from_object(self, ob):
        return jsonify(ob, self.schema, registry=self.registry.jsonify)

    def dict_from_jsondict(self, jsondict):
        return normalize(jsondict, self.schema, registry=self.registry.normalize)

    def dict_from_object(self, ob):
        return dictify(ob, self.schema)

    def object_from_dict(self, params, strict=True):
        return objectify(params, self.schema, self.modellookup, strict=strict)

    def validate_jsondict(self, jsondict):
        return validate(jsondict, self.schema, format_checker=self.format_checker)

    def validate_all_jsondict(self, jsondict):
        return validate_all(jsondict, self.validator)


class MappingFactory(object):
    _Mapping = Mapping
    _ModelLookup = ModelLookup

    def __init__(self, validator_class, schema_factory, module, resolver=None, format_checker=None):
        self.schema_factory = schema_factory
        self.validator_class = validator_class
        self.resolver = resolver
        self.format_checker = format_checker or FormatChecker()
        self.module = module

    def __call__(self, model, includes=None, excludes=None, depth=None):
        schema = self.schema_factory(model, includes=includes, excludes=excludes, depth=depth)
        validator = self.validator_class(schema, resolver=self.resolver, format_checker=self.format_checker)
        modellookup = self._ModelLookup(self.module)
        mapping = self._Mapping(validator, model, modellookup)
        return mapping

Draft3MappingFactory = partial(MappingFactory, Draft3Validator)
Draft4MappingFactory = partial(MappingFactory, Draft4Validator)
