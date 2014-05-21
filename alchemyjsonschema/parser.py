# -*- coding:utf-8 -*-
"""
x -> dict
"""
import json


def from_json(jsonstring):
    return json.loads(jsonstring)


def from_multidict(multidict):
    r = [{}]
    try:
        getter = getattr(multidict, "getall", None) or getattr(multidict, "getlist")
    except AttributeError:
        return multidict  # maybe dict
    for k in multidict.keys():
        for i, v in enumerate(getter(k)):
            try:
                r[i][k] = v
            except IndexError:
                r.append({})
                r[i][k] = v
    if len(r) <= 1:
        return r[0]
    return r


class DjangoMultiDictWrapper(object):
    """almost for testing"""
    def __init__(self, mdict):
        self.mdict = mdict

    def getlist(self, k):
        return self.mdict.getall(k)

    def __getattr__(self, k):
        if k == "getall":
            raise AttributeError(k)
        return getattr(self.mdict, k)
