#!/usr/bin/env -S bash -x
source ../example.rc

# Create a data directory used as static files.
mkdir -p data/sub/deeper
echo "blabla" > data/bla.inp
echo "brrrr" > data/sub/deeper/brrr.inp
echo "works" > data/sub/works.out
echo "fine" > data/fine.out
echo "nested" > data/sub/deeper/nested.out

# Run the example
sb -w -j 1 & # > current_stdout.txt &

# Get the graph after completion of the pending steps.
stepup wait
stepup graph current_graph1
[[ $(wc -l < inventory.jsonl) -eq 4 ]] || exit 1

# A new match of the include pattern makes the inventory step pending.
echo "extra" > data/sub/extra.out
stepup wait -u data/sub/extra.out
stepup rebuild
stepup wait
stepup graph current_graph2
stepup join

# Wait for background processes, if any.
wait

# Check files that are expected to be present and/or missing.
[[ -f plan.py ]] || exit 1
[[ -f inventory.jsonl ]] || exit 1
[[ -f upload.zip ]] || exit 1
[[ $(wc -l < inventory.jsonl) -eq 5 ]] || exit 1
grep -F '"path":"data/sub/extra.out"' inventory.jsonl
