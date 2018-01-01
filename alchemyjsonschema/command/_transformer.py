import inspect


class JSONSchemaTransformer:
    def __init__(self, schema_factory):
        self.schema_factory = schema_factory

    def transform(self, rawtarget, depth):
        if not inspect.isclass(rawtarget):
            raise RuntimeError("please passing the path of model class (e.g. foo.boo:Model)")
        return self.schema_factory(rawtarget, depth=depth)


class Swagger2Transformer:
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
