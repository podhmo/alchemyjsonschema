# -*- coding:utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
Base = declarative_base()


def _getTarget():
    from alchemyjsonschema import SchemaFactory
    return SchemaFactory


def _makeOne(*args, **kwargs):
    return _getTarget()(*args, **kwargs)


def test_detect__nullable_is_True__not_required():
    from alchemyjsonschema import SingleModelWalker

    class Model0(Base):
        __tablename__ = "Model0"
        pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
        created_at = sa.Column(sa.DateTime, nullable=True)

    target = _makeOne(SingleModelWalker)
    walker = target.walker(Model0)
    result = target._detect_required(walker)
    assert result == ["pk"]


def test_detect__nullable_is_False__required():
    from alchemyjsonschema import SingleModelWalker

    class Model1(Base):
        __tablename__ = "Model1"
        pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
        created_at = sa.Column(sa.DateTime, nullable=False)

    target = _makeOne(SingleModelWalker)
    walker = target.walker(Model1)
    result = target._detect_required(walker)
    assert result == ["pk", "created_at"]


def test_detect__nullable_is_False__but_default_is_exists__not_required():
    from alchemyjsonschema import SingleModelWalker
    from datetime import datetime

    class Model2(Base):
        __tablename__ = "Model2"
        pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
        created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.now)

    target = _makeOne(SingleModelWalker)
    walker = target.walker(Model2)
    result = target._detect_required(walker)
    assert result == ["pk"]
