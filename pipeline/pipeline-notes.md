# Recipedia wave 2 pipeline (scripts and worker brief, Nov 20 2026)

Rebuild in a fresh workspace: put recipedia-dishes.csv at data/dishes.csv, recipedia-recipes.csv at data/recipes.csv, write the dish_ids of every recipes-added file to data/wave1_ids.txt, run the batch builder below, then loop: next.py 10 -> one haiku worker per batch -> check.py -> requeue.py. Limits: 200 web searches per turn (10 batches), about 800 page reads an hour (a round every 15 minutes).

## WORKER.md
```
# Recipedia recipe worker

Use only the Read, Write, WebSearch and WebFetch tools. Do not search for, load or call any other tool (no scheduling, no messaging, no ToolSearch).

You find ONE good recipe page for each dish in your batch. Work fast and spend few tokens.

## Input
/home/claude/rx/in/bNNN.json — a list of dishes: dish_id, dish, cuisine, description.

## For each dish
1. One WebSearch (mode "standard"), e.g. `<dish> recipe` (add the cuisine if the name is ambiguous).
2. From the results pick the best recipe page: a full recipe (ingredients and steps) by a named cook or a known food publication. Prefer cooks known for that cuisine, food magazines, newspapers, broadcasters, well-known recipe blogs.
3. Open it with WebFetch. Use this prompt: "Is this a full recipe page with ingredients and steps (yes/no)? Give the exact recipe title, the cook's name as the page states it, the site name, and one specific thing about the method or ingredients that sets this version apart (12 words max)."
4. Keep it only if WebFetch confirms a full recipe for this dish. If not, try the next search result once. At most 2 searches and 3 fetches per dish, then skip it.

Never guess or edit a URL. Only use URLs that appeared in search results and that you opened.

## Do not use
Pinterest, YouTube, TikTok, Instagram, Facebook, Reddit, Quora, forums, Food52 community posts, Yummly or other aggregators, Wikipedia, shopping or restaurant-menu pages, AI-generated recipe sites, pages with no cook and no publication name. Video-only pages are out.

## Skip instead of forcing
Skip a dish when it is not something cooked at home from a recipe (a brand product, a restaurant chain item, a plain ingredient that is bought, not made, a whole meal or event), or when nothing trustworthy turns up. A loose match is worse than a skip.

## Output
Write /home/claude/rx/out/bNNN.jsonl, one JSON object per line, one line per dish (kept or skipped):
{"dish_id":"...","cook":"...","source":"...","recipe_title":"...","note":"...","url":"...","opened":"yes"}
{"dish_id":"...","skip":"short reason"}

- cook: the person named on the page. If the page names no person, use the publication name.
- source: the site or publication name, e.g. "Serious Eats", "BBC Good Food".
- recipe_title: as the page gives it.
- note: 6 to 12 words in your own words, the specific thing that sets this version apart (an ingredient, a technique, a time). Plain, no quotes copied from the page, no "this recipe", no praise words. Examples: "Pork belly braised in soy, cooled overnight before slicing" / "Batter rests an hour; fried twice for a crisp shell".
- url: exactly as opened.

Write the file once, at the end, with the Write tool. Then reply with ONE line only: `bNNN kept K skipped S`.
```

## check.py
```
"""Check worker batches and merge passing rows into merged.csv.
Usage: python3 check.py            -> checks every out/*.jsonl not yet merged
"""
import json, glob, os, re, csv, sys
from urllib.parse import urlparse

BAD = ['pinterest.', 'youtube.', 'youtu.be', 'tiktok.', 'instagram.', 'facebook.', 'reddit.',
       'quora.', 'yummly.', 'wikipedia.', 'food52.com/recipes/community', 'amazon.', 'tasteatlas.']
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
for f in sorted(glob.glob('out/b*.jsonl')):
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
```

## next.py
```
import sys,os,glob
n=int(sys.argv[1]) if len(sys.argv)>1 else 1
started=set(open('started.txt').read().split()) if os.path.exists('started.txt') else set()
allb=sorted([os.path.basename(f)[:-5] for f in glob.glob('in/*.json')],key=lambda b:(b[0]!='r',b))
nxt=[b for b in allb if b not in started][:n]
open('started.txt','a').write(''.join(b+'\n' for b in nxt))
print(' '.join(nxt))
```

## requeue.py
```
import json,re,os,glob
d={}
for f in glob.glob('in/*.json'):
    for x in json.load(open(f)): d[x['dish_id']]=x
lines=open('skipped.tsv').read().splitlines()
keep,retry=[],[]
pat=re.compile(r'limit|rate|budget|not searched|not performed|blocked by|failed to load|client error|could not be opened',re.I)
for l in lines:
    p=l.split('\t')
    (retry if len(p)>=3 and pat.search(p[2]) else keep).append(l)
open('skipped.tsv','w').write('\n'.join(keep)+('\n' if keep else ''))
ids=[l.split('\t')[1] for l in retry]
n=len(glob.glob('in/r*.json'))
for i in range(0,len(ids),15):
    n+=1; json.dump([d[x] for x in ids[i:i+15]],open(f'in/r{n:03d}.json','w'),ensure_ascii=False)
print('requeued',len(ids),'dishes into',(len(ids)+14)//15,'retry batches')
```

## batch builder
```
todo = dishes not in recipes.csv, wave-1 ids, any recipes-added-2 part, or the 8 wave-1 skips; sort by popularity_1_100 desc, cuisine, dish; chunk 15 into in/bNNN.json with dish_id, dish, cuisine, description, popularity_1_100
```
