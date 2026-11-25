#!/usr/bin/env -S bash -x
source ../example.rc

# Run the example
sb -w -j 1 & # > current_stdout.txt &

# Get the graph after completion of the pending steps.
stepup wait
stepup graph current_graph
stepup join

# Wait for background processes, if any.
wait

grep -F "Glob pattern (out/*.txt) registered by step (sd-make-inventory --include 'out/*.txt' -o inventory.jsonl) matches (out/a.txt), which step (echo a > out/a.txt) builds." .stepup/fail.log

# Check files that are expected to be present and/or missing.
[[ -f plan.py ]] || exit 1
[[ -f out/a.txt ]] || exit 1
[[ ! -f inventory.jsonl ]] || exit 1
