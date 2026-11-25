#!/usr/bin/env -S bash -x
source ../example.rc

# Create a data directory used as static files.
mkdir data
echo "one" > data/one.txt
echo "two" > data/two.txt

# Run the example
sb -w -j 2 & # > current_stdout.txt &

# Get the graph after completion of the pending steps.
stepup wait
stepup graph current_graph
stepup join

# Wait for background processes, if any.
wait

# Check files that are expected to be present and/or missing.
[[ -f plan.py ]] || exit 1
[[ -f out/a.txt ]] || exit 1
[[ -f out/run.log ]] || exit 1
[[ -f inventory.jsonl ]] || exit 1
grep -F '"path":"out/a.txt"' inventory.jsonl
grep -F '"path":"data/one.txt"' inventory.jsonl
grep -F '"path":"data/two.txt"' inventory.jsonl
if grep -F run.log inventory.jsonl; then exit 1; fi
[[ $(wc -l < inventory.jsonl) -eq 4 ]] || exit 1
