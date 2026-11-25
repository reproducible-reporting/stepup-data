#!/usr/bin/env python3
from stepup.core.api import run
from stepup.data.api import make_inventory

# A pattern only matches static files, so it cannot select a built file.
run("echo a > out/a.txt", shell=True, out="out/a.txt")
make_inventory("inventory.jsonl", include="out/*.txt")
