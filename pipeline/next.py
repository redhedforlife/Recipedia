import sys,os,glob
n=int(sys.argv[1]) if len(sys.argv)>1 else 1
started=set(open('started.txt').read().split()) if os.path.exists('started.txt') else set()
allb=sorted([os.path.basename(f)[:-5] for f in glob.glob('in/*.json')],key=lambda b:(b[0]!='r',b))
nxt=[b for b in allb if b not in started][:n]
open('started.txt','a').write(''.join(b+'\n' for b in nxt))
print(' '.join(nxt))
