import inspect
import argparse
import magicalimport
from dictknife import loading
from alchemyjsonschema import (
    SchemaFactory,
)
from alchemyjsonschema import (
    StructuralWalker,
    NoForeignKeyWalker,
    ForeignKeyWalker,
)
from alchemyjsonschema import (
    RelationDesicion,
    UseForeignKeyIfPossibleDecision,
)


def detect_walker(x):
    if x == "structural":
        return StructuralWalker
    elif x == "noforeignkey":
        return NoForeignKeyWalker
    elif x == "foreignkey":
        return ForeignKeyWalker
    else:
        raise Exception(x)


def detect_decision(x):
    if x == "default":
        return RelationDesicion()
    elif x == "useforeignkey":
        return UseForeignKeyIfPossibleDecision()
    else:
        raise Exception(x)


class Driver(object):
    def __init__(self, transformer, format):
        self.transformer = transformer
        self.format = format

    def run(self, module_path, filename, depth=None):
        data = self.load(module_path)
        result = self.transformer.transform(data, depth=depth)
        self.dump(result, filename)

    def dump(self, data, filename):
        loading.dumpfile(data, filename, format=self.format)

    def load(self, module_path):
        if ":" in module_path:
            return magicalimport.import_symbol(module_path)
        else:
            return magicalimport.import_module(module_path)


class Transformer(object):
    def __init__(self, schema_factory):
        self.schema_factory = schema_factory

    def transform(self, rawtarget, depth):
        if inspect.isclass(rawtarget):
            return self.transform_by_model(rawtarget, depth)
        else:
            return self.transform_by_module(rawtarget, depth)

    def transform_by_model(self, model, depth):
        definitions = {}
        schema = self.schema_factory(model, depth=depth)
        if "definitions" in schema:
            definitions.update(schema.pop("definitions"))
        definitions[schema['title']] = schema
        return {"definitions": definitions}

    def transform_by_module(self, module, depth):
        subdefinitions = {}
        definitions = {}
        for basemodel in collect_models(module):
            schema = self.schema_factory(basemodel, depth=depth)
            if "definitions" in schema:
                subdefinitions.update(schema.pop("definitions"))
            definitions[schema['title']] = schema
        d = {}
        d.update(subdefinitions)
        d.update(definitions)
        return {"definitions": definitions}


def collect_models(module):
    def is_alchemy_model(maybe_model):
        return hasattr(maybe_model, "__table__") or hasattr(maybe_model, "__tablename__")

    if hasattr(module, "__all__"):
        return [getattr(module, name) for name in module.__all__]
    else:
        return [value for name, value in module.__dict__.items() if is_alchemy_model(value)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help='the module or class to extract schemas from')
    parser.add_argument("--format", default="json", choices=["json", "yaml"])
    parser.add_argument(
        "--walker", choices=["noforeignkey", "foreignkey", "structural"], default="structural"
    )
    parser.add_argument("--decision", choices=["default", "useforeignkey"], default="default")
    parser.add_argument("--depth", default=None, type=int)
    parser.add_argument("--out", default=None, help='output to file')

    args = parser.parse_args()

    walker = detect_walker(args.walker)
    relation_decision = detect_decision(args.decision)

    driver = Driver(
        Transformer(SchemaFactory(walker, relation_decision=relation_decision)),
        format=args.format,
    )
    driver.run(args.target, args.out)
