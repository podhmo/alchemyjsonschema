default: swagger2 jsonschema

swagger2:
	alchemyjsonschema models.py:Group --out dst/default.json
	alchemyjsonschema models.py:Group --out dst/default.yaml

jsonschema:
	alchemyjsonschema models.py:Group --layout=jsonschema --out dst/jsonschema.json

openapi3:
	alchemyjsonschema models.py:Group --layout=openapi3.0 --out dst/openapi3.json
