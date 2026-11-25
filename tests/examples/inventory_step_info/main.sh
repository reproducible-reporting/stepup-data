#!/usr/bin/env -S bash -x
source ../example.rc

# Create the static input of the script.
echo "one" > work/src.txt

# Run the example
sb -w -j 3 & # > current_stdout.txt &

# Get the graph after completion of the pending steps.
stepup wait
stepup graph current_graph1
cp inventory.jsonl current_inventory1.jsonl
grep -F '"path":"work/a.txt"' inventory.jsonl
grep -F '"path":"work/b.txt"' inventory.jsonl
grep -F '"path":"work/src.txt"' inventory.jsonl
if grep -F generate.py inventory.jsonl; then exit 1; fi
[[ $(wc -l < inventory.jsonl) -eq 4 ]] || exit 1

# A change of a listed file changes the digests in the inventory.
echo "two" > work/src.txt
stepup wait -u work/src.txt
stepup rebuild
stepup wait
stepup graph current_graph2
stepup join

# Wait for background processes, if any.
wait

# Check files that are expected to be present and/or missing.
[[ -f plan.py ]] || exit 1
[[ -f gen-info.json ]] || exit 1
[[ -f inventory.jsonl ]] || exit 1
[[ $(wc -l < inventory.jsonl) -eq 4 ]] || exit 1
# Only the header is unchanged, because each listed file has a new digest.
[[ $(grep -Fxc -f current_inventory1.jsonl inventory.jsonl) -eq 1 ]] || exit 1
