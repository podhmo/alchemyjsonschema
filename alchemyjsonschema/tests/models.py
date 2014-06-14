# -*- coding:utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker())

Base = declarative_base()


class Group(Base):
    __tablename__ = "Group"
    query = Session.query_property()

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)
    color = sa.Column(sa.Enum("red", "green", "yellow", "blue"))
    created_at = sa.Column(sa.DateTime, nullable=True)


class User(Base):
    __tablename__ = "User"
    query = Session.query_property()

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(Group.pk), nullable=False)
    group = orm.relationship(Group, uselist=False, backref="users")
    created_at = sa.Column(sa.DateTime, nullable=True)


class A0(Base):
    __tablename__ = "A0"

    name = sa.Column(sa.String(255), default="", nullable=False)
    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")


class A1(Base):
    __tablename__ = "A1"

    name = sa.Column(sa.String(255), default="", nullable=False)
    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key1")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A0.pk), nullable=False)
    parent = orm.relationship(A0, uselist=False, backref="children")


class A2(Base):
    __tablename__ = "A2"

    name = sa.Column(sa.String(255), default="", nullable=False)
    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key2")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A1.pk), nullable=False)
    parent = orm.relationship(A1, uselist=False, backref="children")


class MyModel(Base):
    """regression. case: nullable=False column is not found."""
    __tablename__ = 'models'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text)
    value = sa.Column(sa.Integer)
