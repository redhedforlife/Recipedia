"""Check worker batches and merge passing rows into merged.csv.
Usage: python3 check.py            -> checks every out/*.jsonl not yet merged
"""
import json, glob, os, re, csv, sys
from urllib.parse import urlparse

BAD = ['pinterest.', 'youtube.', 'youtu.be', 'tiktok.', 'instagram.', 'facebook.', 'reddit.',
       'quora.', 'yummly.', 'wikipedia.', 'food52.com/recipes/community', 'amazon.', 'tasteatlas.', 'food52.com/recipes/', 'slurrp.com', 'corriecooks.com', 'flavor365', 'eathealthy365', '.edsqa', 'staging.']
FIELDS = ['dish_id', 'cook', 'source', 'recipe_title', 'note', 'url', 'opened']
known = set(u.strip().rstrip('/').lower() for u in open('data/known_urls.txt') if u.strip())
merged_path = 'merged.csv'
skipped_path = 'skipped.tsv'
done_path = 'done_batches.txt'
done = set(open(done_path).read().split()) if os.path.exists(done_path) else set()
seen = set()
if os.path.exists(merged_path):
    for r in csv.DictReader(open(merged_path)):
        seen.add(r['url'].rstrip('/').lower())

new_rows, new_skips, report, redo = [], [], [], []
for f in sorted(glob.glob('out/*.jsonl')):
    b = os.path.basename(f).split('.')[0]
    if b in done:
        continue
    ids = {x['dish_id'] for x in json.load(open(f'in/{b}.json'))}
    rows, skips, errs = [], [], []
    for line in open(f):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            errs.append('bad json'); continue
        did = o.get('dish_id')
        if did not in ids:
            errs.append(f'unknown id {did}'); continue
        if 'skip' in o:
            skips.append((did, o['skip'])); continue
        u = (o.get('url') or '').strip()
        host = urlparse(u).netloc.lower()
        problem = None
        if not u.startswith('http') or not host:
            problem = 'bad url'
        elif any(x in u.lower() for x in BAD):
            problem = 'blocked site'
        elif u.rstrip('/').lower() in known or u.rstrip('/').lower() in seen:
            problem = 'url already used'
        elif not all((o.get(k) or '').strip() for k in ['cook', 'source', 'recipe_title', 'note']):
            problem = 'blank field'
        elif not (3 <= len(o['note'].split()) <= 16):
            problem = 'note length'
        if problem:
            skips.append((did, 'rejected: ' + problem)); continue
        o['opened'] = 'yes'
        seen.add(u.rstrip('/').lower())
        rows.append({k: o.get(k, '').strip() for k in FIELDS})
    covered = {r['dish_id'] for r in rows} | {s[0] for s in skips}
    missing = ids - covered
    for m in missing:
        skips.append((m, 'not returned'))
    if sum(1 for s in skips if 'budget' in s[1].lower() or 'not performed' in s[1].lower()) >= 2:
        os.remove(f); redo.append(b); report.append(f'{b}: REQUEUED (search budget)'); 
        st=[x for x in open('started.txt').read().split() if x!=b]; open('started.txt','w').write('\n'.join(st)+'\n'); continue
    if errs and len(errs) > 3:
        redo.append(b); report.append(f'{b}: REDO ({len(errs)} errors)'); continue
    new_rows += rows; new_skips += [(b,) + s for s in skips]
    done.add(b)
    report.append(f'{b}: kept {len(rows)} skipped {len(skips)}' + (f' errs {len(errs)}' if errs else ''))

write_header = not os.path.exists(merged_path)
with open(merged_path, 'a', newline='') as fh:
    w = csv.DictWriter(fh, FIELDS)
    if write_header:
        w.writeheader()
    w.writerows(new_rows)
with open(skipped_path, 'a') as fh:
    for s in new_skips:
        fh.write('\t'.join(s) + '\n')
open(done_path, 'w').write('\n'.join(sorted(done)))
tot = sum(1 for _ in csv.DictReader(open(merged_path)))
print('\n'.join(report))
print(f'NEW kept {len(new_rows)} | merged total {tot} | batches done {len(done)} | redo {redo}')
