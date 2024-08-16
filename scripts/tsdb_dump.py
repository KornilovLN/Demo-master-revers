#!/usr/bin/env python
import json
import yaml
import requests
import time
from urllib2 import urlparse
from pathlib import Path
import utils

_Loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)

def construct_cell( loader, tag, conf):
    return loader.construct_mapping(conf)

class Loader(_Loader):
    pass

Loader.add_multi_constructor('!pg:', construct_cell)


class OpenTSDB(object):
    delta_range = 0 # one day in ms

    def __init__(self, url, slice_end=True):
        self.url = url
        self.url_query = urlparse.urljoin(url, '/api/query')
        self.url_suggest = urlparse.urljoin(url, '/api/suggest')
        self.url_last = urlparse.urljoin(url, '/api/query/last')
        self.slice_end = slice_end

    @staticmethod
    def request(url, data, **kw):
        ''' make POST requests to OpenTsdb from http
        '''
        _s = time.time()
        try:
            p = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            r = requests.post(url, data=p, **kw)
            ret = r.json()
            status_code = r.status_code
        except Exception as e:
            status_code = 500
            ret = {"error": {'message': "%s" % e}}

        print 'done', time.time() - _s
        return ret, status_code


    def timeRange(self, start=None, end=None):
        ''' normalize the time range
        '''
        if end is None:
            end = int(time.time() * 1000)
        else:
            end = int(end)
        if start is None:
            start = end - self.delta_range
        else:
            start = int(start)
        return min(start, end), max(start, end)


    def _querie(self, metrics):
        _queries = []
        for uid in metrics:
            q1 = {'aggregator': 'zimsum',
                  'tags': {'a': 'i|e'},
                  'metric': uid
                  }
            q2 = {'aggregator': 'zimsum',
                  'tags': {'a': 's'},
                  'metric': uid
                  }

            _queries.append(q1)
            _queries.append(q2)
        return _queries


    def querie(self, metrics, start=None, end=None):

        try:
            start, end = self.timeRange(start, end)
        except Exception as e:
            return {'error': {'message': e}}, 400

        qstart = max(start - self.delta_range, 0)
        qend   = max(end   + self.delta_range, 0) if self.slice_end else end

        params = {'start': qstart,
                  'end': qend,
                  'queries': self._querie(metrics),
                  'msResolution': False
                  }

        # Step 1: request data
        ret, status_code = self.request(self.url_query, params)
        return ret, status_code


def _joinData(ret):
    r = []
    idxs = {}

    for m in ret:
        if isinstance(m, basestring):
            m = {'metric': m}

        m['id'] = metric = m.pop('metric')
        tag_a = m.pop('tags', {}).get('a')
        dps = m.get('dps', {})

        if tag_a == 'i':
            dps.update({ (int(k) - 1, None) for k in dps.keys() })
        elif tag_a == 'e':
            dps.update({ (int(k) + 1, None) for k in dps.keys() })

        idx = idxs.get(metric)
        if idx is None:
            idxs[metric] = len(r)
            r.append(m)
        else:
            if 'dps' in r[idx]:
                r[idx]['dps'].update(dps)
            else:
                r[idx]['dps'] = dps
    return r


def to_plain(fn, obj):
    z = []
    for i in obj:
        metric = i.get('metric')
        dps = i.get('dps', {})
        tags = i.get('tags', {})
        tags = ' '.join(map(lambda (a, b): '{}={}'.format(a,b), tags.items()))
        for t, v in dps.items():
            z.append('put {} {} {} {}\n'.format(metric, t, v, tags))
    z = sorted(z)
    utils.create_dir(fn)
    with fn.open('wb') as f:
        f.write(''.join(z))


def to_json(fn, obj):
    utils.create_dir(fn)
    with fn.open('wb') as f:
        json.dump(obj, f, sort_keys=True,
            skipkeys=False, ensure_ascii=False, check_circular=False, allow_nan=True,
            indent=1, separators=(',', ':'), encoding='utf-8'
        )


def dump(db, metric, dest):
    fn = Path(dest) / metric
    if fn.is_file():
        print '-', metric
        return
    obj, s = db.querie([metric], start=0)
    if s >= 400:
        print 'Error:', metric, s, obj['error']['message']
        return
    print '.', metric
    to_json(fn, _joinData(obj))
#    to_plain(fn, obj)


def process(db, metrics, dest):
    for metric in metrics:
        dump(db, metric, dest)
        if metric[3] == 'a':
            dump(db, metric+'.S', dest)


def main(db, srs, dest):
    p = Path(srs)
    metrics = set()
    for i in p.glob('*/*.pg'):
        with i.open('rb') as f:
            pg = yaml.load(f, Loader=Loader)
        metrics = metrics | set([i['id'] for i in pg])

    # TODO: here it is necessary to mapped identifiers
    process(db, metrics, dest)



if __name__ == "__main__":
    db = OpenTSDB('http://vavilon:4242')
    main(db, '.rtdb', './.dump/')
