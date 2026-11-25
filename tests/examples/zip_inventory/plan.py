#!/usr/bin/env python3
from stepup.core.api import run, static
from stepup.data.api import make_inventory, zip_inventory

static("static.txt")
run("echo hello > built.txt", out="built.txt", shell=True)
make_inventory("inventory.jsonl", paths=["static.txt", "built.txt"])
zip_inventory("inventory.jsonl", "upload.zip")
