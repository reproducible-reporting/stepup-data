#!/usr/bin/env python3
from stepup.core.api import static
from stepup.data.api import make_inventory, sync_zenodo

static("sync_zenodo.yaml", "zenodo_description.md", "README.txt")
make_inventory("zenodo_inventory.jsonl", paths="README.txt")
sync_zenodo("sync_zenodo.yaml", "zenodo_description.md", "zenodo_inventory.jsonl")
