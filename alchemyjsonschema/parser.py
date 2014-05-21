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

    used = {}
    use_php_compatible_flow = False
    for k in multidict.keys():
        if k in used:
            continue
        used[k] = 1

        if k.endswith("[]"):  # php compatible
            store_k = k[:-2]
            use_php_compatible_flow = True
            for i, v in enumerate(getter(k)):
                try:
                    r[0][store_k].append(v)
                except IndexError:
                    r.append({})
                    r[0].setdefault(store_k, [])
                    r[0][store_k].append(v)
                except KeyError:
                    r[0].setdefault(store_k, [])
                    r[0][store_k].append(v)
        else:
            store_k = k
            for i, v in enumerate(getter(k)):
                try:
                    r[i][store_k] = v
                except IndexError:
                    r.append({})
                    r[i][store_k] = v
    if len(r) <= 1:
        return r[0]
    if use_php_compatible_flow:
        raise Exception("something wrong")
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
