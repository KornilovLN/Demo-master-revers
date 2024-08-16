#! /usr/bin/env python
import yaml
from pathlib import Path
from rdflib import Graph
from copy import copy


def load_data(fn):
    p = Path(fn)
    with p.open('rb') as f:
        data = yaml.load(f)
    return data

Q = '''prefix mof: <http://spd.ivl.cns/cim/rtdbmof#>
select * where {<%s> mof:arr_index ?arr_index; mof:array ?arr}'''


def map_data(src, data):
    graph = Graph()
    graph.parse(src, format="n3")
    ret = {}
    for i in data:
        qres = graph.query(Q % i)
        if qres:
            for r in qres:
                obj = r.asdict()
                arr = obj.get('arr').toPython()
                arr_index = int(obj.get('arr_index').toPython())
                d = copy(data[i])
                d['addr'] = [arr.rsplit('/',1)[-1], arr_index]
                ret[i] = d
        else:
            print 'Warning pp not found: %s' % i

    return ret


def save_data(fn, data):
    p = Path(fn)
    with p.open('wb') as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)


def main():
    data = load_data('./dump/rtdb.yaml')
    data = map_data('.work/demo.ttl', data)
    save_data('.work/rtdb_map.yaml', data)


if __name__=='__main__':
    main()

