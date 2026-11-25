#!/usr/bin/env python3
from stepup.core.api import script, static
from stepup.data.api import make_inventory

static("work/generate.py")
script("generate.py", workdir="work/", step_info="../gen-info.json")
make_inventory(
    "inventory.jsonl",
    include_info_inp="gen-info.json",
    include_info_out="gen-info.json",
    exclude="**/*.py",
)
