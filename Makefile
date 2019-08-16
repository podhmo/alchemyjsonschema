DST=README.rst
default:
	echo alchemyjsonschema > ${DST}
	echo ================= >> ${DST}
	echo "" >> ${DST}
	echo ".. code:: python\n" >> ${DST}
	cat ./demo.py | gsed 's/^\(.\)/   \1/g' >> ${DST}

format:
	black alchemyjsonschema
