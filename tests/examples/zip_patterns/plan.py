#!/usr/bin/env python3
from stepup.core.api import static
from stepup.data.api import make_inventory, zip_inventory

# Make all files in `data` static when they are needed.
static("data/")

make_inventory("inventory.jsonl", include="data/**", exclude="data/**/*.inp")
zip_inventory("inventory.jsonl", "upload.zip")
