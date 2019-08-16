# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.custom.format import validate_date

    return validate_date(*args, **kwargs)


def test_it():
    from datetime import date

    print(date.today().isoformat())
    today = date.today().isoformat()
    result = _callFUT(today)
    assert result is True


def test_it__failure():
    today = "2011-13-13"
    result = _callFUT(today)
    assert result is False


def test_it__failure2():
    today = "2011/12/12"
    result = _callFUT(today)
    assert result is False
