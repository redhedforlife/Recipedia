import json,re,os,glob
d={}
for f in glob.glob('in/*.json'):
    for x in json.load(open(f)): d[x['dish_id']]=x
lines=open('skipped.tsv').read().splitlines()
keep,retry=[],[]
pat=re.compile(r'limit|rate|budget|not searched|not performed|blocked by|failed to load|client error|could not be opened|unverified|rerun|not checked|429',re.I)
for l in lines:
    p=l.split('\t')
    (retry if len(p)>=3 and pat.search(p[2]) else keep).append(l)
open('skipped.tsv','w').write('\n'.join(keep)+('\n' if keep else ''))
ids=[l.split('\t')[1] for l in retry]
n=len(glob.glob('in/r*.json'))
for i in range(0,len(ids),15):
    n+=1; json.dump([d[x] for x in ids[i:i+15]],open(f'in/r{n:03d}.json','w'),ensure_ascii=False)
print('requeued',len(ids),'dishes into',(len(ids)+14)//15,'retry batches')
