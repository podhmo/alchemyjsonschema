# -*- coding:utf-8 -*-
"""
x -> dict
"""
import json


def from_json(jsonstring):
    return json.loads(jsonstring)


def from_multidict(multidict):
    r = [{}]
    getter = getattr(multidict, "getall", None) or getattr(multidict, "getlist")
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
