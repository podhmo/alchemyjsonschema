# -*- coding:utf-8 -*-


def _callFUT(*args, **kwargs):
    from alchemyjsonschema.parser import from_multidict
    return from_multidict(*args, **kwargs)


def test_single():
    from webob.multidict import MultiDict

    mdict = MultiDict({"name": "foo", "country": "jp"})
    result = _callFUT(mdict)

    assert result == {"name": "foo", "country": "jp"}


def test_multiple__convert_to_dict_list__order_also_same():
    from webob.multidict import MultiDict

    mdict = MultiDict([
        ("name", "foo"), ("country", "jp"),
        ("name", "bar"), ("country", "us"),
        ("name", "boo"), ("country", "ch"),
    ])
    result = _callFUT(mdict)
    assert result == [{"name": "foo", "country": "jp"},
                      {"name": "bar", "country": "us"},
                      {"name": "boo", "country": "ch"}]


def test_multiple2__convert_to_dict_list__order_also_same():
    from webob.multidict import MultiDict

    mdict = MultiDict([
        ("name", "foo"), ("name", "bar"), ("name", "boo"),
        ("country", "jp"), ("country", "us"), ("country", "ch"),
    ])
    result = _callFUT(mdict)
    assert result == [{"name": "foo", "country": "jp"},
                      {"name": "bar", "country": "us"},
                      {"name": "boo", "country": "ch"}]
