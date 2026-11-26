"""Turn a PostHog export (pipe-separated rows from the heatmap query) into heat.json and a private copy of the site.
Usage: python3 heat/build.py heat/rows-YYYY-MM-DD.psv   -> heat/out/ (index.html with HEAT_MODE, heat.json, data files)"""
import sys, json, shutil, os, datetime
src = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__)); docs = os.path.join(here, '..', 'docs'); out = os.path.join(here, 'out')
rows = [l.rstrip('\n').split('|') for l in open(src) if l.strip()]
if rows[0][0] in ('L', 'T', 'O'):  # compact export: L|x|y|zoom|secs||cuisine||sid, T|x|y|zoom||hit|||sid, O|||||cuisine|dish||sid
    conv = []
    for r in rows:
        r += [''] * (9 - len(r))
        if r[0] == 'L': conv.append(['Looked at', r[1], r[2], r[3], r[4], '', '', '', r[6], '', r[8], ''])
        elif r[0] == 'T': conv.append(['Tapped plate', r[1], r[2], r[3], '', r[5], '', '', '', '', r[8], ''])
        else: conv.append(['Opened dish', '', '', '', '', '', '', r[6], r[5], '', r[8], ''])
    rows = [['event', 'x', 'y', 'zoom', 'seconds', 'hit', 'name', 'dish', 'cuisine', 'how', 'sid', 'timestamp']] + conv
head, rows = rows[0], rows[1:]
num = lambda v: None if v in ('', '(null)') else float(v)
txt = lambda v: '' if v in ('', '(null)') else v
looks, taps, opens, sessions, stamps = [], [], {}, set(), []
for r in rows:
    e = dict(zip(head, r)); sessions.add(e['sid']); stamps.append(e['timestamp'])
    if e['event'] == 'Looked at' and num(e['x']) is not None: looks.append([num(e['x']), num(e['y']), num(e['zoom']), num(e['seconds']), txt(e['cuisine'])])
    elif e['event'] == 'Tapped plate' and num(e['x']) is not None: taps.append([num(e['x']), num(e['y']), txt(e['hit']), txt(e['name'])])
    elif e['event'] in ('Opened dish', 'Opened recipe') and txt(e['dish']): k = (txt(e['dish']), txt(e['cuisine'])); opens[k] = opens.get(k, 0) + 1
fmt = lambda t: datetime.datetime.fromisoformat(t.replace('Z', '+00:00')).strftime('%b %-d')
stamps = [t for t in stamps if t]
rng = f"{fmt(min(stamps))} to {fmt(max(stamps))}" if stamps else (sys.argv[2] if len(sys.argv) > 2 else '')
heat = {'meta': {'range': rng, 'sessions': len(sessions), 'built': datetime.date.today().isoformat()}, 'looks': looks, 'taps': taps, 'opens': [[d, c, n] for (d, c), n in opens.items()]}
os.makedirs(out, exist_ok=True)
json.dump(heat, open(os.path.join(out, 'heat.json'), 'w'), separators=(',', ':'))
html = open(os.path.join(docs, 'index.html')).read().replace('<head>', '<head>\n<script>window.HEAT_MODE = true;</script>', 1)
open(os.path.join(out, 'index.html'), 'w').write(html)
for f in ('data.json', 'globe.json', 'd3.min.js'): shutil.copy(os.path.join(docs, f), os.path.join(out, f))
print(f"{len(looks)} looks, {len(taps)} taps, {sum(opens.values())} opens, {len(sessions)} visits, {rng}")
