# -*- coding:utf-8 -*-
def _getTarget():
    from alchemyjsonschema import SchemaFactory
    return SchemaFactory


def _makeOne(walker, *args, **kwargs):
    from alchemyjsonschema import DefaultClassfier
    return _getTarget()(walker, DefaultClassfier, *args, **kwargs)


# definition
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Group(Base):
    """model for test"""
    __tablename__ = "Group"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)


class User(Base):
    __tablename__ = "User"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=True)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(Group.pk), nullable=False)
    group = orm.relationship(Group, uselist=False, backref="users")


def test_properties__default__includes__foreign_keys():
    from alchemyjsonschema import SingleModelWalker
    target = _makeOne(SingleModelWalker)
    result = target(User)

    assert "properties" in result
    assert list(sorted(result["properties"].keys())) == ["group_id", "name", "pk"]


def test_properties__include_OnetoMany_relation():
    from alchemyjsonschema import AlsoChildrenWalker, RelationDesicion
    target = _makeOne(AlsoChildrenWalker, relation_decision=RelationDesicion())
    result = target(User)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["group", "name", "pk"]
    assert result["properties"]["group"] == {"$ref": "#/definitions/Group"}


def test_properties__include_OnetoMany_relation2():
    from alchemyjsonschema import AlsoChildrenWalker, ComfortableDesicion
    target = _makeOne(AlsoChildrenWalker, relation_decision=ComfortableDesicion())
    result = target(User)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["group_id", "name", "pk"]
    assert result["properties"]["group_id"] == {'type': 'integer', "relation": "group"}


def test_properties__include_ManytoOne_backref():
    from alchemyjsonschema import AlsoChildrenWalker
    target = _makeOne(AlsoChildrenWalker)
    result = target(Group)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["name", "pk", "users"]
    assert result["properties"]["users"] == {"type": "array", "items": {"$ref": "#/definitions/User"}}
    assert result["definitions"]["User"] == {"type": "object", 'required': ['pk'],
                                             "properties": {'name': {'maxLength': 255, 'type': 'string'},
                                                            'pk': {'description': 'primary key', 'type': 'integer'}}}


def test_properties__include_ManytoOne_backref__bidirectional_is_true():
    from alchemyjsonschema import AlsoChildrenWalker, ChildFactory
    target = _makeOne(AlsoChildrenWalker, child_factory=ChildFactory(".", bidirectional=True))
    result = target(Group)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["name", "pk", "users"]
    assert result["properties"]["users"] == {"type": "array", "items": {"$ref": "#/definitions/User"}}
    assert result["definitions"]["User"] == {"type": "object", 'required': ['pk'],
                                             "properties": {'name': {'maxLength': 255, 'type': 'string'},
                                                            'group': {'$ref': '#/definitions/Group'},
                                                            'pk': {'description': 'primary key', 'type': 'integer'}}}


# depth
class A0(Base):
    __tablename__ = "A0"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")


class A1(Base):
    __tablename__ = "A1"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key1")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A0.pk), nullable=False)
    parent = orm.relationship(A0, uselist=False, backref="children")


class A2(Base):
    __tablename__ = "A2"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key2")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A1.pk), nullable=False)
    parent = orm.relationship(A1, uselist=False, backref="children")


class A3(Base):
    __tablename__ = "A3"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key3")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A2.pk), nullable=False)
    parent = orm.relationship(A2, uselist=False, backref="children")


class A4(Base):
    __tablename__ = "A4"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key4")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A3.pk), nullable=False)
    parent = orm.relationship(A3, uselist=False, backref="children")


class A5(Base):
    __tablename__ = "A5"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key5")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A4.pk), nullable=False)
    parent = orm.relationship(A4, uselist=False, backref="children")


def test_properties__default_depth_is__traverse_all_chlidren():
    from alchemyjsonschema import AlsoChildrenWalker
    from alchemyjsonschema.dictify import get_reference
    target = _makeOne(AlsoChildrenWalker)
    result = target(A0)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["children", "pk"]
    children0 = get_reference(result["properties"]["children"]["items"], result)
    children1 = get_reference(children0["properties"]["children"]["items"], result)
    children2 = get_reference(children1["properties"]["children"]["items"], result)
    children3 = get_reference(children2["properties"]["children"]["items"], result)
    children4 = get_reference(children3["properties"]["children"]["items"], result)
    assert children4["properties"]["pk"]["description"] == "primary key5"


def test_properties__default_depth_is__2__traverse_depth2():
    from alchemyjsonschema import AlsoChildrenWalker
    from alchemyjsonschema.dictify import get_reference
    target = _makeOne(AlsoChildrenWalker)
    result = target(A0, depth=2)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["children", "pk"]
    children0 = get_reference(result["properties"]["children"]["items"], result)
    assert children0["properties"]["pk"]["description"] == "primary key1"


def test_properties__default_depth_is__3__traverse_depth3():
    from alchemyjsonschema import AlsoChildrenWalker
    from alchemyjsonschema.dictify import get_reference
    target = _makeOne(AlsoChildrenWalker)
    result = target(A0, depth=3)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["children", "pk"]
    children0 = get_reference(result["properties"]["children"]["items"], result)
    children1 = get_reference(children0["properties"]["children"]["items"], result)
    assert children1["properties"]["pk"]["description"] == "primary key2"


# regression
# X.y -> Y.z -> Z.y -> Y.z -> Z.y

class Y(Base):
    __tablename__ = "y"
    id = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    z_id = sa.Column(sa.Integer, sa.ForeignKey('z.id'))
    zs = orm.relationship("Z", foreign_keys=[z_id])


class X(Base):
    __tablename__ = "x"
    id = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    y_id = sa.Column(sa.Integer, sa.ForeignKey('y.id'))
    ys = orm.relationship(Y, foreign_keys=[y_id])


class Z(Base):
    __tablename__ = "z"
    id = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    y_id = sa.Column(sa.Integer, sa.ForeignKey('y.id'))
    ys = orm.relationship(Y, foreign_keys=[y_id])


def test_properties__infinite_loop():
    from alchemyjsonschema import AlsoChildrenWalker, RelationDesicion
    from alchemyjsonschema.dictify import get_reference
    target = _makeOne(AlsoChildrenWalker, relation_decision=RelationDesicion())
    result = target(X)
    ys = result["properties"]["ys"]
    zs = get_reference(ys, result)["properties"]["zs"]
    xs = get_reference(zs, result)["properties"]
    assert "required" in result
    assert list(sorted(result["properties"])) == ["id", "ys"]
    assert xs["id"]["description"] == "primary key"


def test_properties__infinite_loop2():
    from alchemyjsonschema import AlsoChildrenWalker, ComfortableDesicion
    target = _makeOne(AlsoChildrenWalker, relation_decision=ComfortableDesicion())
    result = target(X)
    assert "required" in result
    assert list(sorted(result["properties"])) == ["id", "y_id"]

    assert result["properties"]["y_id"] == {"type": "integer", "relation": "ys"}
