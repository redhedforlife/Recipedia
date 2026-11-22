"""Append recipe rows from a CSV to app/data.json.

Usage: python3 pipeline/add_recipes.py path/to/new.csv
CSV columns: dish_id, cook, source, recipe_title, note, url

Skips rows whose dish_id is unknown, whose url is already in the app, or whose
url is not http(s). Applies the standard cook-name fixes. Prints a summary.
Recipe rows in data.json are [dish_index, title, cook, source, url, note].
"""
import csv, json, sys

FIXES = {'Ciao Italia': 'Mary Ann Esposito', 'Emeril Live': 'Emeril Lagasse',
         'Emerils.com': 'Emeril Lagasse', 'Chinese Cooking Demystified': 'Steph Li and Chris Thompson',
         'Dimitra Khan': 'Dimitra Alexandrakis'}
BLOCK = ['pinterest.', 'youtube.', 'youtu.be', 'tiktok.', 'instagram.', 'facebook.', 'reddit.',
         'quora.', 'yummly.', 'wikipedia.', 'food52.com/recipes/community', 'amazon.', 'tasteatlas.',
         'slurrp.', 'flavor365.', '/tag/', '/category/']

path = 'app/data.json'
d = json.load(open(path))
idx = {x[0]: i for i, x in enumerate(d['D'])}
have = {r[4] for r in d['Rc']}
added, bad = 0, {'unknown dish': 0, 'duplicate url': 0, 'bad url': 0, 'blocked site': 0}
for r in csv.DictReader(open(sys.argv[1], encoding='utf-8-sig')):
    u = (r.get('url') or '').strip()
    cook = (r.get('cook') or '').strip()
    src = (r.get('source') or '').strip()
    if r.get('dish_id') not in idx: bad['unknown dish'] += 1; continue
    if not u.startswith('http'): bad['bad url'] += 1; continue
    if any(b in u.lower() for b in BLOCK): bad['blocked site'] += 1; continue
    if u in have: bad['duplicate url'] += 1; continue
    if 'justonecookbook.com' in u: cook, src = 'Namiko Chen', 'Just One Cookbook'
    if 'thewoksoflife.com' in u and cook in ('Judy', 'Bill', 'Sarah', 'Kaitlin'): cook += ' Leung'
    cook = FIXES.get(cook, cook) or src
    have.add(u)
    d['Rc'].append([idx[r['dish_id']], (r.get('recipe_title') or '').strip(), cook, src, u, (r.get('note') or '').strip()])
    added += 1
json.dump(d, open(path, 'w'), separators=(',', ':'), ensure_ascii=False)
print(f"added {added}; skipped {bad}; recipes now {len(d['Rc'])}; dishes with a recipe {len({x[0] for x in d['Rc']})} of {len(d['D'])}")
