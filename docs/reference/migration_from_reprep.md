---
description: >-
  How to move a project from the inventory tools and the Zenodo synchronization
  of StepUp RepRep 4.2 to StepUp Data 4.3,
  with the renamed, rewritten, dropped and added features.
---

<!--
SPDX-FileCopyrightText: 2026 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# From StepUp RepRep 4.2 to StepUp Data 4.3

StepUp Data takes over the inventory tools and the Zenodo synchronization
of [StepUp RepRep 4.2](https://reproducible-reporting.github.io/stepup-reprep/).
The other features of StepUp RepRep, such as the compilation of documents and the PDF tools,
are not part of StepUp Data.

The files that StepUp RepRep 4.2 wrote are accepted unchanged:
inventories, Zenodo configuration files and record-id files.
A project only needs changes in `plan.py`, in scripts that call the commands,
and in the environment that holds the Zenodo token.

## Renamed

Install `stepup-data` and replace the following names:

| StepUp RepRep 4.2 | StepUp Data |
|---|---|
| `stepup.reprep.api.make_inventory()` | `stepup.data.api.make_inventory()` |
| `stepup.reprep.api.zip_inventory()` | `stepup.data.api.zip_inventory()` |
| `stepup.reprep.api.sync_zenodo()` | `stepup.data.api.sync_zenodo()` |
| `stepup.reprep.inventory` | `stepup.data.inventory` |
| `stepup.reprep.pytest` | `stepup.data.pytest` |
| `srr-make-inventory` | `sd-make-inventory` |
| `srr-check-inventory` | `sd-check-inventory` |
| `srr-zip-inventory` | `sd-zip-inventory` |
| `srr-sync-zenodo` | `sd-sync-zenodo` |
| `REPREP_ZENODO_TOKEN` | `STEPUP_DATA_ZENODO_TOKEN` |

The functions are documented in the [API reference](../reference/stepup.data.api.md).

`REPREP_ZENODO_TOKEN` has no effect in StepUp Data.
Without `STEPUP_DATA_ZENODO_TOKEN`, `sync_zenodo()` only prints a warning and uploads nothing,
so rename the variable wherever it is set, e.g. in `.envrc` or in CI secrets.

## Rewritten

### `make_inventory()`

The inventory output file is now the first argument,
and the files to include in the inventory are passed with the keyword argument `paths`:

```python
# StepUp RepRep 4.2
make_inventory("a.txt", "b.txt", "inventory.jsonl")

# StepUp Data
make_inventory("inventory.jsonl", paths=["a.txt", "b.txt"])
```

A call written for StepUp RepRep 4.2 always raises an error.
The command `sd-make-inventory` keeps its interface,
apart from the removal of `-i` described [below](#dropped).

### `zip_inventory()`

The second argument is renamed from `path_zip` to `dest` and is now optional:

```python
zip_inventory("inventory.jsonl")  # writes inventory.zip
zip_inventory("inventory.jsonl", "archive/")  # writes archive/inventory.zip
zip_inventory("inventory.jsonl", "dataset.zip")  # same as in StepUp RepRep 4.2
```

The inventory must have suffix `.jsonl` and the ZIP file must have suffix `.zip`.
The files listed in the inventory are now inputs of the step,
so the ZIP file is rebuilt when one of them changes, even when the inventory stays the same.

### `sync_zenodo()`

Only the name of the module and of the token variable changed, see [Renamed](#renamed).

## Dropped

Inventory definition files (`inventory.def`) are no longer supported.
This removes the argument `path_def` of `make_inventory()`
and the option `-i` of `sd-make-inventory`.
Their rules looked for files in places that StepUp does not track,
such as the directory listing, the git index or the database of a workflow,
so an inventory could miss files or depend on the number of parallel jobs.
Replace each rule as follows:

| Rule in `inventory.def` | Replacement in StepUp Data |
|---|---|
| `include PATTERN` | `include="PATTERN"`, relative to the directory of `plan.py` |
| `exclude PATTERN` | `exclude="PATTERN"` |
| `include-git` | List the files in `plan.py`, or archive the sources with `git archive` |
| `include-workflow` | List the outputs by name, or use `include_info_out`, see [Added](#added) |

[Archive a Git Repository](../tutorials/archive_git.md) explains how to use `git archive`.

For example, a definition file in the same directory as `plan.py`:

```text
include data/**
exclude data/**/*.tmp
```

becomes:

```python
make_inventory("inventory.jsonl", include="data/**", exclude="data/**/*.tmp")
```

Patterns now follow the rules of `glob()` in StepUp Core:
they only match static files, and a pattern that matches nothing is an error.
Files built by other steps must be listed by name, or through step info files.
See [Selecting Files](../tutorials/inventory_files.md#selecting-files) for the details.

## Added

- The arguments `include` and `exclude` of `make_inventory()`,
  and the options `--include` and `--exclude` of `sd-make-inventory`,
  select files with patterns or literal paths.
- The arguments `include_info_inp` and `include_info_out` of `make_inventory()`,
  and the options `--include-info-inp` and `--include-info-out` of `sd-make-inventory`,
  add the inputs or outputs listed in step info files,
  see [Files Listed in Step Info Files](../tutorials/inventory_files.md#files-listed-in-step-info-files).
- `hash_algorithm=None` of `make_inventory()` and `--hash none` of `sd-make-inventory`
  write an inventory without digests, which is faster for large datasets.
  Such an inventory cannot be used by `sync_zenodo()`,
  and StepUp RepRep 4.2 cannot read it.
- `STEPUP_DATA_ZENODO_TOKEN` is registered with StepUp Core,
  so `stepup config` lists it without showing its value.

The [changelog](../changelog.md) lists all changes per release.
