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


CTX = dict([(val, key) for key, val in PREFIXES.iteritems()])


class PGLoader(yaml.SafeLoader):

    @staticmethod
    def construct_cell(loader, tag, conf):
        m = loader.construct_mapping(conf)
        m['kind'] = tag
        return m

PGLoader.add_multi_constructor('!pg:', PGLoader.construct_cell)


def get_pref(uri):
    ns = uri.rsplit('/', 1)[0]
    pref = CTX.get('{}/'.format(ns))
    if pref is None:
        print '#####', uri, CTX
    return pref


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


def load_data(fn):
    p = Path(fn)
    with p.open('rb') as f:
        data = yaml.load(f)
    return data


def push_values(root_path, data):
    root_path = Path(root_path)
    nss = {}
    for pp in sorted(data.keys()):
        ns = get_pref(pp)
        m = nss.get(ns)
        if m is None:
            m = RTDB(root_path / ns)
            nss[ns] = m
        item = data[pp]
        m.set(**item)


def push():
    root = '.work/rtdb'
    data = load_data('.work/rtdb_map.yaml')
    data = push_values(root, data)


if __name__=='__main__':
    push()
