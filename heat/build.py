"""Turn a PostHog export (pipe-separated rows from the heatmap query) into heat.json and a private copy of the site.
Usage: python3 heat/build.py heat/rows-YYYY-MM-DD.psv   -> heat/out/ (index.html with HEAT_MODE, heat.json, data files)"""
import sys, json, shutil, os, datetime
src = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__)); docs = os.path.join(here, '..', 'docs'); out = os.path.join(here, 'out')
rows = [l.rstrip('\n').split('|') for l in open(src) if l.strip()]
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
rng = f"{fmt(min(stamps))} to {fmt(max(stamps))}" if stamps else ''
heat = {'meta': {'range': rng, 'sessions': len(sessions), 'built': datetime.date.today().isoformat()}, 'looks': looks, 'taps': taps, 'opens': [[d, c, n] for (d, c), n in opens.items()]}
os.makedirs(out, exist_ok=True)
json.dump(heat, open(os.path.join(out, 'heat.json'), 'w'), separators=(',', ':'))
html = open(os.path.join(docs, 'index.html')).read().replace('<head>', '<head>\n<script>window.HEAT_MODE = true;</script>', 1)
open(os.path.join(out, 'index.html'), 'w').write(html)
for f in ('data.json', 'globe.json', 'd3.min.js'): shutil.copy(os.path.join(docs, f), os.path.join(out, f))
print(f"{len(looks)} looks, {len(taps)} taps, {sum(opens.values())} opens, {len(sessions)} visits, {rng}")
