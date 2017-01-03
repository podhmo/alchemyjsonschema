# -*- coding:utf-8 -*-
import os


from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.txt')) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''

install_requires = [
    'setuptools',
    'sqlalchemy',
    'jsonschema',
    'strict-rfc3339',
    'isodate',  # hmm.
    'pytz'
]

docs_extras = [
]

tests_require = [
    "pytest",
    "webob"
]

testing_extras = tests_require + [
]

from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


setup(name='alchemyjsonschema',
      version='0.4.2',
      description='mapping jsonschema for sqlalchemy models',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: Implementation :: CPython",
      ],
      keywords='alchemyjsonschema sqlalchemy jsonschema schema-generation',
      author="podhmo",
      author_email="",
      url="https://github.com/podhmo/alchemyjsonschema",
      packages=find_packages(exclude=["alchemyjsonschema.tests"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={
          'testing': testing_extras,
          'docs': docs_extras,
      },
      tests_require=tests_require,
      cmdclass={'test': PyTest},
      license="mit",
      entry_points="""
      [console_scripts]
      alchemyjsonschema = alchemyjsonschema.command:main
      """
)
