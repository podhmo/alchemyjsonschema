import magicalimport
from dictknife import loading
from alchemyjsonschema import SchemaFactory
from alchemyjsonschema import StructuralWalker, NoForeignKeyWalker, ForeignKeyWalker
from alchemyjsonschema import RelationDesicion, UseForeignKeyIfPossibleDecision
from ._transformer import (
    JSONSchemaTransformer,
    OpenAPI2Transformer,
    OpenAPI3Transformer,
)


def detect_walker_factory(x):
    if x == "structural":
        return StructuralWalker
    elif x == "noforeignkey":
        return NoForeignKeyWalker
    elif x == "foreignkey":
        return ForeignKeyWalker
    else:
        raise ValueError(x)


def detect_decision(x):
    if x == "default":
        return RelationDesicion()
    elif x == "useforeignkey":
        return UseForeignKeyIfPossibleDecision()
    else:
        raise ValueError(x)


def detect_transformer(layout):
    if layout in ("swagger2.0", "openapi2.0"):
        return OpenAPI2Transformer
    elif layout == "openapi3.0":
        return OpenAPI3Transformer
    elif layout == "jsonschema":
        return JSONSchemaTransformer
    else:
        raise ValueError(layout)


class Driver:
    def __init__(self, walker, decision, layout):
        self.transformer = self.build_transformer(walker, decision, layout)

    def build_transformer(self, walker, decision, layout):
        walker_factory = detect_walker_factory(walker)
        relation_decision = detect_decision(decision)
        schema_factory = SchemaFactory(
            walker_factory, relation_decision=relation_decision
        )
        transformer_factory = detect_transformer(layout)
        return transformer_factory(schema_factory).transform

    def run(self, module_path, filename, format, depth=None):
        data = self.load(module_path)
        result = self.transformer(data, depth=depth)
        self.dump(result, filename, format=format)

    def dump(self, data, filename, format):
        loading.setup(loading.json.load, loading.json.dump)
        loading.dumpfile(data, filename, format=format, sort_keys=True)

    def load(self, module_path):
        if ":" in module_path:
            return magicalimport.import_symbol(module_path)
        else:
            return magicalimport.import_module(module_path)
