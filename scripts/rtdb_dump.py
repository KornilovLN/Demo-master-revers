#! /usr/bin/env python
import yaml
from pathlib import Path
from pyrtdb import PyProcessMemory


PREFIXES = {
    "z1":  "http://spd.znpp.cns/ivs/z1/",
    "z2":  "http://spd.znpp.cns/ivs/z2/",
    "z3":  "http://spd.znpp.cns/ivs/z3/",
    "z4":  "http://spd.znpp.cns/ivs/z4/",
    "z5":  "http://spd.znpp.cns/ivs/z5/",
    "z6":  "http://spd.znpp.cns/ivs/z6/",
    "za":  "http://spd.znpp.cns/za/",
    "zr":  "http://spd.znpp.cns/svrk/",
    "zpams": "http://spd.znpp.cns/pams/",
    "zrd": "http://spd.znpp.cns/rodos/",
}


CTX = {(val, key) for val, key in PREFIXES.iteritems()}


class PGLoader(yaml.SafeLoader):

    @staticmethod
    def construct_cell(loader, tag, conf):
        m = loader.construct_mapping(conf)
        m['kind'] = tag
        return m

PGLoader.add_multi_constructor('!pg:', PGLoader.construct_cell)


def get_url(uid):
    pref, uid = uid.split('.', 1)
    c = PREFIXES.get(pref)
    return '{}{}'.format(c, uid)


class RTDB(object):
    mem = None
    def __init__(self, path):
        if path:
            self.open(path)
 
    def open(self, path):
        memf = Path(path) / 'memory'
        self.mem = PyProcessMemory(str(memf))

    def get(self, addr, kind, *args, **kw):
        arrid, idx = addr
        arr = self.mem.find(arrid)
        cell = arr.data[idx - 1]
        if arr.arrtype == ord('A'):
            ret = dict(value=cell.value, status=cell.status)
        elif kind=='B2':
            cell2 = arr.data[idx]
            ret = dict(status=cell.status, status2=cell2.status)
        else:
            ret = dict(status=cell.status)
        return ret

    def set(self, addr, *args, **kw):
        arrid, idx = addr
        arr = self.mem.find(arrid)
        cell = arr.data[idx - 1]
        if 'status' in kw:
            cell.status = kw.get('status')
        if 'value' in kw:
            cell.value = kw.get('value')
        if 'status2' in kw:
            cell2 = arr.data[idx]
            cell2.status = kw.get('status2')


def save_data(fn, data):
    p = Path(fn)
    with p.open('wb') as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)


def indexpg(root_path):
    p = Path(root_path)
    index = {}
    for fn in p.glob('*/f*.pg'):
        if fn.is_file():
            with fn.open('rb') as f:
                pgitems = yaml.load(f, Loader=PGLoader)
                for item in pgitems:
                    uid = item.get('id')
                    index[uid] = dict(addr=item['addr'], kind=item['kind'])
    return index


def pull_values(root_path, index):
    root_path = Path(root_path)
    nss = {}
    ret = {}
    for pp in sorted(index.keys()):
        ns = pp.split('.', 1)[0]
        m = nss.get(ns)
        if m is None:
            m = RTDB(root_path / ns)
            nss[ns] = m
        ret[get_url(pp)] = m.get(**index[pp])
    return ret


def dump():
    root = './.rtdb'
    index = indexpg(root)
    data = pull_values(root, index)
    save_data('./dump/rtdb.yaml', data)


if __name__=='__main__':
    dump()
