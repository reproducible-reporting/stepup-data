---
description: >-
  Release notes for every version of StepUp Data,
  following Keep a Changelog and effort-based versioning.
---

<!--
SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Effort-based Versioning](https://jacobtomlinson.dev/effver/).
(Changes to features documented as "experimental" will not increment macro and meso version numbers.)

## [Unreleased][]

(no changes yet)

## [4.3.0a0][] - 2026-11-25 {: #v4.3.0a0 }

This first development release takes over the inventory tools
and the Zenodo synchronization of StepUp RepRep 4.2,
under new names and with the changes listed below.
Inventories written by StepUp RepRep 4.2 can be read and checked without changes,
and its Zenodo configuration files and record-id files are used without changes.

### Added

- The environment variable `STEPUP_DATA_ZENODO_TOKEN` is registered with StepUp Core,
  so `stepup config` lists it without showing its value.
- The arguments `include` and `exclude` of `make_inventory()`,
  and the options `--include` and `--exclude` of `sd-make-inventory`,
  select files with patterns,
  see [Selecting Files](tutorials/inventory_files.md#selecting-files).
- The arguments `include_info_inp` and `include_info_out` of `make_inventory()`,
  and the options `--include-info-inp` and `--include-info-out` of `sd-make-inventory`,
  add the inputs or outputs listed in step info files to an inventory,
  see [Files Listed in Step Info Files](tutorials/inventory_files.md#files-listed-in-step-info-files).
- The option `--hash none` of `sd-make-inventory`,
  and `hash_algorithm=None` of `make_inventory()`, write an inventory without digests,
  see [Hash Algorithm](tutorials/inventory_files.md#hash-algorithm).
  `sd-check-inventory` and `sd-zip-inventory` then only check the sizes,
  permission bits and link targets.

### Changed

- The module `stepup.reprep.inventory`, which defines the format of inventories,
  is now `stepup.data.inventory`.
- The functions [`make_inventory()`][stepup.data.api.make_inventory]
  and [`zip_inventory()`][stepup.data.api.zip_inventory] of `stepup.reprep.api`
  are now in `stepup.data.api`.
- The commands `srr-make-inventory`, `srr-check-inventory` and `srr-zip-inventory`
  are now `sd-make-inventory`, `sd-check-inventory` and `sd-zip-inventory`.
- The pytest helpers of `stepup.reprep.pytest`, which mask the permission bits in inventories,
  are now in `stepup.data.pytest`.
- The function [`sync_zenodo()`][stepup.data.api.sync_zenodo] of `stepup.reprep.api`
  is now in `stepup.data.api`, and the command `srr-sync-zenodo` is now `sd-sync-zenodo`,
  see [Synchronize a Zenodo Dataset](tutorials/sync_zenodo.md).
- The Zenodo token is taken from the environment variable `STEPUP_DATA_ZENODO_TOKEN`.
  The environment variable `REPREP_ZENODO_TOKEN` has no effect.
- `sd-zip-inventory` amends the listed files as inputs of its step,
  so the ZIP file is rebuilt when a file changes, even when its inventory stays the same.
- `make_inventory(dest, *, paths=())` replaces `make_inventory(*paths)`,
  whose last positional argument was the inventory to write.
  The files to list are now given as `paths`, like the other arguments that select files,
  e.g. `make_inventory("inventory.jsonl", paths=["a.txt", "b.txt"])`.
  A call written for StepUp RepRep 4.2 raises an error instead of being misread.
- `zip_inventory(path_inventory, dest=None)` replaces `zip_inventory(path_inventory, path_zip)`.
  By default, the ZIP file is written next to the inventory, with suffix `.zip`,
  as with `sd-zip-inventory`, and `dest` may also be a directory.

### Removed

- Inventory definition files (`inventory.def`),
  the option `-i` of `sd-make-inventory` and the argument `path_def` of `make_inventory()`.
  Their rules looked for files in places that StepUp does not track,
  such as the directory listing, the git index or the database of a workflow,
  so an inventory could miss files or depend on the number of parallel jobs.
  The rules of a definition file are replaced as follows:
    - `include PATTERN` becomes `include="PATTERN"`,
      with the pattern now relative to the directory of `plan.py`,
      not to that of the definition file.
    - `exclude PATTERN` becomes `exclude="PATTERN"`.
    - `include-git`: list the files in `plan.py`,
      or archive the sources with `git archive`.
    - `include-workflow`: list the outputs by name,
      e.g. from the `StepInfo` returned by the step that builds them.

[Unreleased]: https://github.com/reproducible-reporting/stepup-data
[4.3.0a0]: https://github.com/reproducible-reporting/stepup-data/releases/tag/v4.3.0a0
