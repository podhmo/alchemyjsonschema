# -*- coding:utf-8 -*-
"""
support: passing model's object.
https://github.com/podhmo/alchemyjsonschema/issues/8
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def _getTarget():
    from alchemyjsonschema import SchemaFactory
    return SchemaFactory


def _makeOne(*args, **kwargs):
    from alchemyjsonschema import (
        SingleModelWalker,
    )
    return _getTarget()(SingleModelWalker)


class TestTable(Base):
    __tablename__ = "TestTable"

    firstnumber = sa.Column(sa.Integer, primary_key=True)
    secondnumber = sa.Column(sa.Integer)
    bez = sa.Column(sa.String(50), default="", nullable=True)


def test_it():
    engine = sa.create_engine("sqlite:///:memory:")
    Base.metadata.bind = engine
    Base.metadata.create_all()
    session = orm.Session(engine)

    session.add(TestTable(firstnumber=1, secondnumber=1, bez="test"))
    session.commit()
    row = session.query(TestTable).first()

    result = _makeOne()(row)
    print(result)
