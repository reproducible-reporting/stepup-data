---
title: Data Exchange and Archiving
description: >-
  StepUp Data is a StepUp extension that records the data files of a project in inventories,
  packs them into ZIP files and keeps them in sync with a Zenodo record.
---

<!--
SPDX-FileCopyrightText: 2026 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

<!-- The front matter sets the HTML title of the page, not a second heading. -->
<!-- pyml disable-num-lines 3 single-title -->

# StepUp Data: Data Exchange and Archiving

<!-- snipwise.md BEGIN abstract -->
StepUp Data helps you manage data files of a research project.
It records them in inventories, packs them into ZIP files and keeps them in sync with Zenodo.
As an extension of [StepUp Core](https://reproducible-reporting.github.io/stepup-core/),
a universal dynamic build tool,
it performs these tasks as build steps that rerun only when their inputs change.
StepUp Data is part of [Reproducible Reporting](https://github.com/reproducible-reporting).
<!-- snipwise.md END abstract -->

!!! warning "StepUp Data is in early development, and its API may still change."

    For production use, keep using
    [StepUp RepRep 4.2](https://reproducible-reporting.github.io/stepup-reprep/).

    The section [From StepUp RepRep 4.2 to StepUp Data 4.3](reference/migration_from_reprep.md)
    lists all changes to the API.

## Overview

StepUp Data collects the files of a project into datasets that can be exchanged and archived.
Inventories are the common basis of all its features:

- An [inventory](tutorials/inventory_files.md) lists the files of a dataset
  with their sizes and digests, so that copies of the files can be checked at any time.
  `make_inventory()` writes an inventory as a step of a StepUp workflow,
  and `sd-check-inventory` checks files against it.
- Files that the workflow builds are added to an inventory by name,
  or through the step info files that other steps write.
  A step info file lists the inputs and outputs of a step
  that are only known when the step runs,
  so that the inventory follows the step without listing its files by hand.
  See [Files Listed in Step Info Files](tutorials/inventory_files.md#files-listed-in-step-info-files).
- `zip_inventory()` packs the files of an inventory into a reproducible ZIP file,
  see [Creating a ZIP Archive](tutorials/inventory_files.md#creating-a-zip-archive-from-an-inventoryjsonl-file).
- `sync_zenodo()` keeps the files of an inventory in sync with a draft dataset on Zenodo,
  together with its metadata,
  see [Synchronize a Zenodo Dataset](tutorials/sync_zenodo.md).

[Archive a Git Repository](tutorials/archive_git.md)
explains how to deposit the history and the sources of a project as static files.
