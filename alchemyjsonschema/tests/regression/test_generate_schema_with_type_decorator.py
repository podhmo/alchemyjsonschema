# -*- coding:utf-8 -*-


def _callFUT(*args, **kwargs):
    # see: https://github.com/podhmo/alchemyjsonschema/issues/6
    from alchemyjsonschema import SchemaFactory, StructuralWalker

    factory = SchemaFactory(StructuralWalker)
    return factory(*args, **kwargs)


def _makeType(impl_):
    from sqlalchemy.types import TypeDecorator

    class Choice(TypeDecorator):
        impl = impl_

        def __init__(self, choices, **kw):
            self.choices = dict(choices)
            super(Choice, self).__init__(**kw)

        def process_bind_param(self, value, dialect):
            return [k for k, v in self.choices.iteritems() if v == value][0]

        def process_result_value(self, value, dialect):
            return self.choices[value]

    return Choice


def test_it():
    import sqlalchemy as sa
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.types import String

    Base = declarative_base()
    Choice = _makeType(impl_=String)

    class Hascolor(Base):
        __tablename__ = "hascolor"
        hascolor_id = sa.Column(sa.Integer, primary_key=True)
        candidates = [(c, c) for c in ["r", "g", "b", "y"]]
        color = sa.Column(Choice(choices=candidates, length=1), nullable=False)

    result = _callFUT(Hascolor)
    assert result["properties"]["color"] == {"type": "string", "maxLength": 1}


def test_it__impl_is_not_callable():
    import sqlalchemy as sa
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.types import String

    Base = declarative_base()
    Choice = _makeType(impl_=String(length=1))

    class Hascolor(Base):
        __tablename__ = "hascolor"
        hascolor_id = sa.Column(sa.Integer, primary_key=True)
        candidates = [(c, c) for c in ["r", "g", "b", "y"]]
        color = sa.Column(Choice(choices=candidates), nullable=False)

    result = _callFUT(Hascolor)
    assert result["properties"]["color"] == {"type": "string", "maxLength": 1}
