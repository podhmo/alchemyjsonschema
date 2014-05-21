# -*- coding:utf-8 -*-


def _callFUT(*args, **kwargs):
    from alchemyjsonschema.parser import from_multidict
    return from_multidict(*args, **kwargs)


def test_dict__return_onesself():
    mdict = {"name": "foo", "country": "jp"}
    result = _callFUT(mdict)

    assert result == {"name": "foo", "country": "jp"}


def test_single_mdict__return_dict():
    from webob.multidict import MultiDict

    mdict = MultiDict({"name": "foo", "country": "jp"})
    result = _callFUT(mdict)

    assert result == {"name": "foo", "country": "jp"}


def test_django_like_mdict__return_dict():
    from webob.multidict import MultiDict
    from alchemyjsonschema.parser import DjangoMultiDictWrapper

    mdict = DjangoMultiDictWrapper(MultiDict({"name": "foo", "country": "jp"}))
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


def test_php_compatible_mdict_return_list():
    from webob.multidict import MultiDict

    mdict = MultiDict([("name", "foo"), ("g_id[]", "1"), ("g_id[]", "2")])
    result = _callFUT(mdict)
    assert result == {"name": "foo", "g_id": ["1", "2"]}
