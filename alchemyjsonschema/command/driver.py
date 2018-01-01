import magicalimport
from dictknife import loading
from alchemyjsonschema import SchemaFactory
from ._transformer import Transformer


class Driver:
    def __init__(self, walker, decision, format):
        self.walker = walker
        self.decision = decision
        self.format = format

    def build_transformer(self):
        schema_factory = SchemaFactory(self.walker, relation_decision=self.decision)
        return Transformer(schema_factory).transform

    def run(self, module_path, filename, depth=None):
        transformer = self.build_transformer()
        data = self.load(module_path)
        result = transformer(data, depth=depth)
        self.dump(result, filename)

    def dump(self, data, filename):
        loading.dumpfile(data, filename, format=self.format)

    def load(self, module_path):
        if ":" in module_path:
            return magicalimport.import_symbol(module_path)
        else:
            return magicalimport.import_module(module_path)
