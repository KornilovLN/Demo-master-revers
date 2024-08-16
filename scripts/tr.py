# -* coding: utf-8 -*-

from lxml import etree as ET
from utils import need_tr, create_dir
from pathlib import Path
import polib
import json

ENCODING = "utf-8"
POT_FILENAME = '.locale/messages.pot'

SVG_NS = 'http://www.w3.org/2000/svg'
XLINK_NS = 'http://www.w3.org/1999/xlink'
NSS = {"svg": SVG_NS,
       "xlink": XLINK_NS
       }
XTITLE = '{http://www.w3.org/1999/xlink}title'
XHREF =  '{http://www.w3.org/1999/xlink}href'

STORE = polib.POFile(encoding=ENCODING, check_for_duplicates=True)
STORE.metadata.setdefault('Content-Type', 'text/plain; charset=%s' % ENCODING)
STORE.metadata.setdefault('X-Poedit-SourceCharset', ENCODING)


def remove_knop(svg, mnemos):
    find_knop = ET.XPath('//svg:a[@class="knop"]', namespaces=NSS)
    for knop in find_knop(svg):
        href = knop.get(XHREF)
        if href and href[2:] not in mnemos:
            knop.getparent().remove(knop)
    return svg


def append(msgid, msgstr="", msgctxt=None, occurrences=None):
    entry = polib.POEntry(msgid=msgid, msgstr=msgstr, msgctxt=msgctxt)
    if occurrences:
        entry.occurrences = occurrences[:]
    try:
        STORE.append(entry)
    except ValueError:
        preventry = STORE.find(msgid, msgctxt=msgctxt)
        if preventry.occurrences and occurrences:
            for oc in preventry.occurrences:
                if oc not in entry.occurrences:
                    entry.occurrences.append(oc)
        if preventry:
            preventry.merge(entry)


def extract_text(svg, ctx):
    find_text = ET.XPath('//svg:text', namespaces=NSS)
    find_title = ET.XPath('//svg:title', namespaces=NSS)
    find_tspan = ET.XPath('//svg:tspan', namespaces=NSS)
    els = find_text(svg) + find_title(svg) + find_tspan(svg)
    for el in els:
        text = el.text
        if text is None:
            continue
        text = text.strip()
        msgctxt = el.attrib.get('msgctxt')
        if need_tr(text):
            append(text, msgctxt=msgctxt, occurrences=[(ctx.get('id'), 1)])

    find_attr_title = ET.XPath('//svg:a[@xlink:title]', namespaces=NSS)
    els = find_attr_title(svg)
    for el in els:
        text = el.attrib.get(XTITLE)
        if text is None:
            continue
        text = text.strip()
        msgctxt = el.attrib.get('msgctxt')
        if need_tr(text):
            append(text, msgctxt=msgctxt, occurrences=[(ctx.get('id'), 2)])


def process_svg(data, mnemos, ctx):
    mnemo = data['mnemo']
    svg = ET.fromstring(mnemo)
    svg = remove_knop(svg, mnemos)
    extract_text(svg, ctx)
    data['mnemo'] = ET.tostring(svg, encoding=ENCODING).decode(ENCODING)
    return data


def save_mnemo(fn, obj):
    dest_fn = Path(fn)
    create_dir(dest_fn)
    with dest_fn.open('w', encoding=ENCODING) as f:
        txt = json.dumps(obj, ensure_ascii=False, separators=(',', ':'), check_circular=False)
        f.write(txt)

def process_rdf(graph):
    for prop in ['rtdbmof:title', 'rtdbmof:mu']:
        row = graph.query('select ?text where { ?pp %s ?text }' % prop)
        for i in row:
            text = i.text.value
            if need_tr(text):
                append(text)

    for prop in ['rtdbmof:states', 'rtdbmof:hints']:
        row = graph.query('select ?text where { ?pp %s ?text }' % prop)
        for i in row:
            for text in json.loads(i.text.value).values():
                if need_tr(text):
                    append(text)


def commit(filename=POT_FILENAME):
    create_dir(filename)
    def cm(a):
        l = a.msgid.split(':', 1)
        return l[::-1]
    STORE.sort(key=cm)
    STORE.save(filename)

