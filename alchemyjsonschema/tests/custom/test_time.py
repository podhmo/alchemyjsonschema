# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.custom.format import validate_time
    return validate_time(*args, **kwargs)


def test_it1():
    from datetime import time
    now = time(10, 20, 30).isoformat() + "Z"
    result = _callFUT(now)
    assert result is True


def test_it2():
    from datetime import time
    now = time(10, 20, 30).isoformat() + ".809840Z"
    result = _callFUT(now)
    assert result is True


def test_it3():
    from datetime import time
    now = time(10, 20, 30).isoformat() + ".809840+10:20"
    result = _callFUT(now)
    assert result is True


def test_it4():
    from datetime import time
    now = time(10, 20, 30).isoformat() + ".809840-10:20"
    result = _callFUT(now)
    assert result is True

