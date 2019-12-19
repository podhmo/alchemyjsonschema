DST=README.rst

test:
	py.test -s -v

default:
	echo alchemyjsonschema > ${DST}
	echo ================= >> ${DST}
	echo "" >> ${DST}
	echo ".. code:: python\n" >> ${DST}
	cat ./demo.py | gsed 's/^\(.\)/   \1/g' >> ${DST}

format:
	black alchemyjsonschema

build:
#	pip install wheel
	python setup.py bdist_wheel

upload:
#	pip install twine
	twine check dist/alchemyjsonschema-$(shell cat VERSION)*
	twine upload dist/alchemyjsonschema-$(shell cat VERSION)*

.PHONY: build upload
