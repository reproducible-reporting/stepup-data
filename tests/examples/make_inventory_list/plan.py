#!/usr/bin/env python3

from stepup.core.api import static
from stepup.data.api import make_inventory

static("README.txt")
make_inventory("inventory.jsonl", paths="README.txt")
