#!/usr/bin/env python3
from stepup.core.api import run, static
from stepup.data.api import make_inventory

static("data/")

# Built files are listed by name, also when they are excluded afterwards.
run("echo a > out/a.txt", shell=True, out="out/a.txt")
run("sleep 1; echo log > out/run.log", shell=True, out="out/run.log")
make_inventory(
    "inventory.jsonl",
    paths="out/a.txt",
    include=["out/run.log", "data/*.txt"],
    exclude="**/*.log",
)
