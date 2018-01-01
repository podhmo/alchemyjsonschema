default: swagger2 jsonschema

swagger2:
	alchemyjsonschema models.py:Group --out dst/default.json
	alchemyjsonschema models.py:Group --out dst/default.yaml

jsonschema:
	alchemyjsonschema models.py:Group --layout=jsonschema --out dst/jsonschema.json
