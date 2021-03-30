# DST=README.rst

# doc:
# 	echo alchemyjsonschema > ${DST}
# 	echo ================= >> ${DST}
# 	echo "" >> ${DST}
# 	echo ".. code:: python\n" >> ${DST}
# 	cat ./demo.py | gsed 's/^\(.\)/   \1/g' >> ${DST}

test:
	pytest -s -v alchemyjsonschema

format:
	black alchemyjsonschema

build:
#	pip install wheel
	python setup.py sdist bdist_wheel

ci:
	$(MAKE) lint test
	git diff

lint:
#	pip install -e .[dev]
	# stop the build if there are Python syntax errors or undefined names
	flake8 prestring --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 prestring --count --ignore W503,E203,E501 --exit-zero --max-complexity=10 --max-line-length=127 --statistics

upload:
#	pip install twine
	twine check dist/alchemyjsonschema-$(shell cat VERSION)*
	twine upload dist/alchemyjsonschema-$(shell cat VERSION)*

.PHONY: build upload
