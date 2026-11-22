import os
s=open('started.txt').read().split()
done=set(open('done_batches.txt').read().split())
held=set(open('handoff/batches.txt').read().split()) if os.path.exists('handoff/batches.txt') else set()
keep=[b for b in s if os.path.exists(f'out/{b}.jsonl') or b in done or b in held]
open('started.txt','w').write('\n'.join(keep)+'\n')
print('returned to queue:',sorted(set(s)-set(keep)))
