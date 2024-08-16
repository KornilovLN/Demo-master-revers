import yaml
from rdflib import URIRef, Literal, Graph
from tr import *


class Gtext(object):
    _locale = {}
    domain = 'messages'
    localedir = 'translations'
    lang = 'en'
    _translator = None

    def translator(self, domain=None, lang=None, localedir=None):
        domain = domain or self.domain
        lang = lang or self.lang
        localedir = localedir or self.localedir
        l = (localedir, lang, domain)
        if l not in self._locale:
            tr_fn = '{}/{}/LC_MESSAGES/{}.po'.format(*l)
            self._locale[l] = polib.pofile(tr_fn, check_for_duplicates=True)
        return self._locale[l]

    def gettext(self, text, msgctxt=None):
        tr = self._translator or self.translator()
        t = tr.find(text, msgctxt=msgctxt)
        if t and t.msgstr:
#             print text, '\t', t.msgstr
            return t.msgstr
        return text

cat = Gtext()
_ = cat.gettext


def _svg(mnemo):
    svg = ET.fromstring(mnemo)
    find_text = ET.XPath('//svg:text', namespaces=NSS)
    find_title = ET.XPath('//svg:title', namespaces=NSS)
    find_tspan = ET.XPath('//svg:tspan', namespaces=NSS)
    els = find_text(svg) + find_title(svg) + find_tspan(svg)
    for el in els:
        t = el.text
        if t:
            text = t.strip()
            msgctxt = el.attrib.get('msgctxt')
            el.text = _(text, msgctxt=msgctxt)

    t = svg.attrib.get(XTITLE)
    if t:
        text = t.strip()
        svg.attrib[XTITLE] = _(text)

    find_attr_title = ET.XPath('//svg:a[@xlink:title]', namespaces=NSS)
    els = find_attr_title(svg)
    for el in els:
        t = el.attrib.get(XTITLE)
        if t:
            text = t.strip()
            el.attrib[XTITLE] = _(text)

    return ET.tostring(svg, encoding=ENCODING).decode(ENCODING)


def _mnemo_data(data):
    for d in data:
        for k in ['title', 'mu']:
            if k in d:
                d[k] = _(d[k])
    return data


def _rdf_type(t):
    ctx = {'rtdbmof': 'http://spd.ivl.cns/cim/rtdbmof#',
        }
    pref, uid = t.split(':')
    g = ctx.get(pref)
    return URIRef(g+uid)


def _tr_dict(obj):
    for key, val in obj.iteritems():
        obj[key] = _(val)
    return obj


def rdf(src, dest, lang=None):
    # TODO: it is not verified
    graph = Graph()
    graph.parse(src, format="n3")
    new_graph = Graph()

    for prop in ['rtdbmof:title', 'rtdbmof:mu']:
        row = graph.query('select * where { ?pp %s ?text }' % prop)
        for i in row:
            text = _(i.text.value)
            if i.text.value != text:
                new_graph.add((i.pp, _rdf_type(prop), Literal(text, lang=lang)))

    for prop in ['rtdbmof:states', 'rtdbmof:hints']:
        row = graph.query('select * where { ?pp %s ?text }' % prop)
        for i in row:
            obj = json.loads(i.text.value)
            text = json.dumps(_tr_dict(obj), sort_keys=True, ensure_ascii=False, check_circular=False, indent=0)
            if i.text.value != text:
                new_graph.add((i.pp, _rdf_type(prop), Literal(text, lang=lang)))

    with Path(dest).open('wb') as f:
        new_graph.serialize(f, format='n3')


def _nav_tr(tree):
    if isinstance(tree, list):
        for c in tree:
            _nav_tr(c)
    elif isinstance(tree, dict):
        if 'text' in tree:
            tree['text'] = _(tree['text'])
        if 'children' in tree:
            _nav_tr(tree['children'])
    return tree


def nav(src, dest):
    with Path(src).open('rb') as f:
        nav = yaml.safe_load(f)
    _nav_tr(nav)
    create_dir(dest)
    with Path(dest).open('wb') as f:
        f.write(json.dumps(nav, indent=2, ensure_ascii=False).encode('utf-8'))


def states(src, dest):
    with Path(src).open('rb') as f:
        st = json.load(f)

    for t in st.values():
        for key in ['hints', 'states']:
            if key in t:
                t[key] = _tr_dict(t[key])

    create_dir(dest)
    with Path(dest).open('wb') as f:
        f.write(json.dumps(st, indent=2, ensure_ascii=False).encode('utf-8'))


def mnemo(src, dest):
    for f in Path(src).glob('*/f*.json'):
#         print '.', f.as_posix()
        dest_fn = dest / f.relative_to(src)
        d = json.load(f.open())
        d['mnemo'] = _svg(d['mnemo'])
        d['data'] = _mnemo_data(d['data'])
        d['title'] = _(d['title'])
        save_mnemo(dest_fn, d)


if __name__=='__main__':
    cat.lang = 'en'
    mnemo('.work/spd', '.work/spd/%s' % cat.lang)
    rdf('.work/demo.ttl', '.work/demo_%s.ttl' % cat.lang, cat.lang)
    nav('.work/nav.yaml', '.work/spd/%s/nav.json'% cat.lang)
    states('.work/spd/meta/mofstates.json', '.work/spd/%s/meta/mofstates.json'% cat.lang)
