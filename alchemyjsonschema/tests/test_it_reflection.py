# -*- coding:utf-8 -*-
import pytest
from collections import OrderedDict

# using sqlalchemy's automap


@pytest.fixture(scope="module")
def db():
    import os.path
    from sqlalchemy.ext.automap import automap_base
    from sqlalchemy import create_engine

    dbname = os.path.join(os.path.abspath(os.path.dirname(__file__)), "reflection.db")
    engine = create_engine("sqlite:///{}".format(dbname))
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    return Base


def _getTarget():
    from alchemyjsonschema import SchemaFactory

    return SchemaFactory


def _makeOne(*args, **kwargs):
    from alchemyjsonschema import StructuralWalker

    return _getTarget()(StructuralWalker)


def test_it(db):
    target = _makeOne()
    schema = target(db.classes.artist)
    expected = {
        "title": "artist",
        "properties": OrderedDict(
            [
                ("artistid", {"type": "integer"}),
                ("artistname", {"type": "string"}),
                (
                    "track_collection",
                    {"items": {"$ref": "#/definitions/track"}, "type": "array"},
                ),
            ]
        ),
        "definitions": {
            "track": {
                "properties": OrderedDict(
                    [
                        ("trackid", {"type": "integer"}),
                        ("trackname", {"type": "string"}),
                    ]
                ),
                "required": ["trackid"],
                "type": "object",
            }
        },
        "type": "object",
        "required": ["artistid"],
    }
    assert schema == expected


def test_it2(db):
    target = _makeOne()
    schema = target(db.classes.track)
    expected = {
        "title": "track",
        "properties": OrderedDict(
            [
                ("trackid", {"type": "integer"}),
                ("trackname", {"type": "string"}),
                ("artist", {"$ref": "#/definitions/artist"}),
            ]
        ),
        "definitions": {
            "artist": {
                "properties": OrderedDict(
                    [
                        ("artistid", {"type": "integer"}),
                        ("artistname", {"type": "string"}),
                    ]
                ),
                "required": ["artistid"],
                "type": "object",
            }
        },
        "type": "object",
        "required": ["trackid"],
    }
    assert schema == expected
