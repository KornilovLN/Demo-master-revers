#! /usr/bin/env python
import json
import yaml
import shutil
from collections import OrderedDict
from pathlib import Path
from ekatra.tools.orderedyaml import load
from rdflib import RDF, Namespace, URIRef, Literal, Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
import tr

sparql_endpoint = SPARQLStore('http://meta:8890/sparql')
TYPE = RDF.type
META = Namespace('http://spd.ivl.cns/cim/meta#')
MMI = Namespace('http://spd.ivl.cns/cim/mmi#')
HIKA = Namespace('http://spd.ivl.cns/cim/hika#')
showon = MMI.showon
MetaGraph = META.graph
MetaPrefix = META.prefix
GroupAlarm = HIKA.GroupAlarm


def _represent_dict(dumper, data):
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', data)

yaml.add_representer(OrderedDict, _represent_dict, Dumper=yaml.SafeDumper)


mnemos = {}
G = Graph()
G.bind('rtdbmof', Namespace('http://spd.ivl.cns/cim/rtdbmof#'))
G.bind('mmi', MMI)
G.bind('h', HIKA)

_gs_ = {}

def get_graph_ns(prefix):
    r = _gs_.get(prefix)
    if r is None:
        r = _gs_[prefix] = Namespace(str(sparql_endpoint.triples((None, MetaPrefix, Literal(prefix))).next()[0][0])+'/')
        G.bind(prefix, r)
    return r


_nodes_ = set()
_fragments_ = set()


def process_node(url):
    if url not in _nodes_:
        triples = [x[0] for x in sparql_endpoint.triples((url, None, None))]
        skip = False
        for triple in triples:
            if triple[1] == TYPE:
                skip = triple[2] == GroupAlarm
                break
        if skip:
            return
        for triple in triples:
            if triple[1] == showon:
                if triple[2] not in _fragments_:
                    continue
            G.add(triple)
            if isinstance(triple[2], URIRef):
                process_node(triple[2])


def load_pg(topic):
    topic = topic.split('.')
    p = Path('.work/rtdb') / topic[2] / '{}.pg'.format(topic[4])
    dir = p.parent
    if not dir.exists():
        dir.mkdir(parents=True)
    shutil.copy('/var/ekatra/rtdb/{}/{}.pg'.format(topic[2], topic[4]), p.as_posix())
    mem = dir / 'memory'
    if not mem.exists():
        shutil.copy('/rtdb/{}/memory'.format(topic[2]), mem.as_posix())


def process_states():
    p = Path('/var/ekatra/spd/meta/mofstates.json')
    if p.exists():
        t = Path('.work/spd/meta/mofstates.json')
        dir = t.parent
        if not dir.exists():
            dir.mkdir(parents=True)
        shutil.copy(p.as_posix(), t.as_posix())


def load_mnemo(conf):
    mnemo = conf['id']
    p = Path('.work/spd') / (mnemo+'.json')
    dir = p.parent
    if not dir.exists():
        dir.mkdir(parents=True)
    shutil.copy('/var/ekatra/spd/{}.json'.format(mnemo), p.as_posix())
    with p.open('r') as f:
        m = json.load(f)
    if 'defaults' not in conf:
        conf['text'] = m['title']
    # with p.with_suffix('.yaml').open('wb') as f:
    #     yaml.safe_dump(m, f, allow_unicode=True, default_flow_style=False)
    for topic in m['topics']:
        load_pg(topic)
    mnemo = mnemo.split('/')
    ns = get_graph_ns(mnemo[0])
    _fragments_.add(ns[mnemo[1]])
    return m


def import_mnemos(conf):
    if isinstance(conf, list):
        for c in conf:
            import_mnemos(c)
    elif isinstance(conf, dict):
        if 'id' in conf:
            mnemos[conf['id']] = conf
        if 'title' in conf:
            conf['text'] = conf['title']
            del conf['title']
        if 'children' in conf:
            m = import_mnemos(conf['children'])


def process_mnemos():
    ms = set(mnemos.iterkeys())
    # print ms
    for mnemo, conf in mnemos.iteritems():
        m = load_mnemo(conf)
        obj = tr.process_svg(m, ms, conf)
        p = Path('.work/spd') / (mnemo+'.json')
        tr.save_mnemo(p, obj)


def process_fragments():
    for fragment in _fragments_:
        process_node(fragment)
        for x in sparql_endpoint.triples((None, showon, fragment)):
            process_node(x[0][0])
    with Path('.work/demo.ttl').open('wb') as f:
        G.serialize(f, format='n3')


def main():
    if not Path('.work').is_dir():
        Path('.work').mkdir()
    p = Path('nav_task.yaml')
    with p.open('rb') as f:
        nav = load(f)
    process_states()
    import_mnemos(nav)
    process_mnemos()
    process_fragments()
    tr.process_rdf(G)
    tr.commit()
    with p.with_name('.work/nav.yaml').open('wb') as f:
        yaml.safe_dump(nav, f, allow_unicode=True, default_flow_style=False)
    p = Path('.work/spd/nav.json')
    with p.open('wb') as f:
        f.write(json.dumps(nav, indent=2, ensure_ascii=False).encode('utf-8'))



if __name__=='__main__':
    main()
