import re, json, urllib.request, html

BASE = 'C:/Users/Administrator/Desktop/cc-main/cc-main/cc-main_extracted/doupo-app'
src = open(BASE + '/client/src/components/TechniqueSigil.vue', encoding='utf-8').read()
block = src.split('const SIGILS = {', 1)[1].split('\n}', 1)[0]

KEY_RE = re.compile(r"^\s{2}'?([a-z0-9-]+)'?\s*:\s*\[", re.M)
ITEM_RE = re.compile(r"\{([^{}]*)\}")

sigil_html = {}
keys = [(m.start(), m.group(1)) for m in KEY_RE.finditer(block)]
for i, (pos, key) in enumerate(keys):
    start = block.index('[', pos)
    depth = 0
    end = start
    for j in range(start, len(block)):
        if block[j] == '[':
            depth += 1
        elif block[j] == ']':
            depth -= 1
            if depth == 0:
                end = j
                break
    body = block[start + 1:end]
    shapes = []
    for sm in ITEM_RE.finditer(body):
        raw = sm.group(1)
        d = re.search(r"\bd:\s*'([^']*)'", raw)
        c = re.search(r"\bc:\s*\[([^\]]+)\]", raw)
        e = re.search(r"\be:\s*\[([^\]]+)\]", raw)
        r2 = re.search(r"\br2:\s*\[([^\]]+)\]", raw)
        sw = re.search(r"\bsw:\s*([\d.]+)", raw)
        st = bool(re.search(r"\bstroke:\s*true", raw))
        swv = float(sw.group(1)) if sw else 2.2
        if d:
            shapes.append({'k': 'path', 'd': d.group(1), 'st': st, 'sw': swv})
        elif c:
            cc = [float(x) for x in c.group(1).split(',')]
            r = re.search(r"\br:\s*([\d.]+)", raw)
            shapes.append({'k': 'circle', 'c': cc, 'r': float(r.group(1)) if r else 1, 'st': st, 'sw': swv})
        elif e:
            ee = [float(x) for x in e.group(1).split(',')]
            rx = re.search(r"\brx:\s*([\d.]+)", raw)
            ry = re.search(r"\bry:\s*([\d.]+)", raw)
            shapes.append({'k': 'ellipse', 'e': ee,
                           'rx': float(rx.group(1)) if rx else 0,
                           'ry': float(ry.group(1)) if ry else 0,
                           'st': st, 'sw': swv})
        elif r2:
            rr = [float(x) for x in r2.group(1).split(',')]
            shapes.append({'k': 'rect', 'r': rr, 'st': st, 'sw': swv})
        else:
            shapes.append({'k': 'unknown', 'raw': raw})
    sigil_html[key] = shapes

print("解析到印记数:", len(sigil_html))
unk = [(k, s['raw']) for k, v in sigil_html.items() for s in v if s['k'] == 'unknown']
if unk:
    print("无法解析的笔画:", unk[:5])

techs = json.load(urllib.request.urlopen('http://localhost:3000/api/world/techniques', timeout=8))['data']

bad = []
ALLOWED = set('MZLHVCSQTAmlzhlvcsqtam')
for t in techs:
    key = t['sigil']
    if key not in sigil_html:
        bad.append((t['name'], key, 'missing'))
        continue
    for s in sigil_html[key]:
        if s['k'] == 'path':
            illegal = set(re.findall(r'[A-Za-z]', s['d'])) - ALLOWED
            if illegal:
                bad.append((t['name'], key, 'cmd:' + ''.join(sorted(illegal))))
            if not s['d'].strip():
                bad.append((t['name'], key, 'empty path'))
        elif s['k'] == 'circle' and s['r'] <= 0:
            bad.append((t['name'], key, 'bad circle r'))
        elif s['k'] == 'ellipse' and (s['rx'] <= 0 or s['ry'] <= 0):
            bad.append((t['name'], key, 'bad ellipse rx/ry'))
        elif s['k'] == 'rect' and (s['r'][2] <= 0 or s['r'][3] <= 0):
            bad.append((t['name'], key, 'bad rect'))
print("几何异常:", bad if bad else "无")


def svg_for(key, color, gid):
    parts = []
    for s in sigil_html.get(key, []):
        if s['k'] == 'path':
            fill = 'none' if s['st'] else 'url(#%s)' % gid
            stroke = 'url(#%s)' % gid if s['st'] else 'none'
            parts.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"/>' % (s['d'], fill, stroke, s['sw']))
        elif s['k'] == 'circle':
            fill = 'none' if s['st'] else 'url(#%s)' % gid
            stroke = 'url(#%s)' % gid if s['st'] else 'none'
            parts.append('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (s['c'][0], s['c'][1], s['r'], fill, stroke, s['sw']))
        elif s['k'] == 'ellipse':
            fill = 'none' if s['st'] else 'url(#%s)' % gid
            stroke = 'url(#%s)' % gid if s['st'] else 'none'
            parts.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (s['e'][0], s['e'][1], s['rx'], s['ry'], fill, stroke, s['sw']))
        elif s['k'] == 'rect':
            fill = 'none' if s['st'] else 'url(#%s)' % gid
            stroke = 'url(#%s)' % gid if s['st'] else 'none'
            parts.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (s['r'][0], s['r'][1], s['r'][2], s['r'][3], fill, stroke, s['sw']))
    return ('<svg viewBox="0 0 48 48"><defs><linearGradient id="%s" x1="0" y1="0" x2="0.35" y2="1">'
            '<stop offset="0%%" stop-color="#ffffff" stop-opacity=".9"/><stop offset="55%%" stop-color="%s"/>'
            '<stop offset="100%%" stop-color="%s" stop-opacity=".5"/></linearGradient></defs>%s</svg>') % (gid, color, color, ''.join(parts))


rows = []
for i, t in enumerate(techs):
    color = t.get('attributeColor') or '#d9b44a'
    rows.append('<div class="c">%s<b>%s</b><span>%s</span></div>' % (
        svg_for(t['sigil'], color, 'g%d' % i), html.escape(t['name']), html.escape(t['sigil'])))

doc = ('<html><head><meta charset="utf-8"><style>body{background:#141018;color:#eee;font-family:system-ui;padding:20px}'
       '.g{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}'
       '.c{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:10px;text-align:center}'
       '.c svg{width:58px;height:58px;filter:drop-shadow(0 0 6px rgba(255,150,60,.5))}'
       '.c b{display:block;font-size:13px;margin-top:6px}.c span{font-size:10px;opacity:.45}</style></head><body>'
       '<div class="g">' + ''.join(rows) + '</div></body></html>')
open('C:/Users/Administrator/Desktop/cc-main/sigil-preview.html', 'w', encoding='utf-8').write(doc)
print("预览已生成: sigil-preview.html (全部 %d 条)" % len(techs))
