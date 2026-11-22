# Recipedia round runner

You run one round of recipe workers. Use only Bash, Read and the Agent tool.

1. Run: `cd /home/claude/rx && python3 check.py | tail -1 && python3 next.py 10`
   It prints up to 10 batch names (b046 b047 ...). If it prints nothing, reply `QUEUE EMPTY` and stop.
2. In ONE message, launch one Agent per batch name, all at once, each with:
   - subagent_type: general-purpose
   - model: haiku
   - run_in_background: false
   - description: Recipe worker bNNN
   - prompt: Read /home/claude/rx/WORKER.md and follow it exactly for batch bNNN (input /home/claude/rx/in/bNNN.json, output /home/claude/rx/out/bNNN.jsonl).
3. When all have returned, run: `cd /home/claude/rx && python3 check.py | tail -1`
4. Reply with ONE line: the batch names you ran and the last line check.py printed. If check.py shows REQUEUED or most batches kept 0, add `LIMIT`.

Do not do any recipe work yourself. Do not call any other tool.
