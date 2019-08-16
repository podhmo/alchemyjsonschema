DST=README.rst

test:
	py.test -s -v

default:
	echo alchemyjsonschema > ${DST}
	echo ================= >> ${DST}
	echo "" >> ${DST}
	echo ".. code:: python\n" >> ${DST}
	cat ./demo.py | gsed 's/^\(.\)/   \1/g' >> ${DST}
