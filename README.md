<!--
SPDX-FileCopyrightText: 2026 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: LGPL-3.0-or-later
-->

# StepUp Data

[![pytest](https://github.com/reproducible-reporting/stepup-data/actions/workflows/pytest.yaml/badge.svg?branch=main)](https://github.com/reproducible-reporting/stepup-data/actions/workflows/pytest.yaml)
[![docs](https://github.com/reproducible-reporting/stepup-data/actions/workflows/docs.yaml/badge.svg?branch=main)](https://github.com/reproducible-reporting/stepup-data/actions/workflows/docs.yaml)
![LGPL-3 License](https://img.shields.io/badge/License-LGPL_v3-blue.svg)

<!-- snipwise.md BEGIN abstract -->
StepUp Data helps you manage data files of a research project.
It records them in inventories, packs them into ZIP files and keeps them in sync with Zenodo.
As an extension of [StepUp Core](https://reproducible-reporting.github.io/stepup-core/),
a universal dynamic build tool,
it performs these tasks as build steps that rerun only when their inputs change.
StepUp Data is part of [Reproducible Reporting](https://github.com/reproducible-reporting).
<!-- snipwise.md END abstract -->

> **Note:** StepUp Data is in early development, and its API may still change.
> For production use, keep using [StepUp RepRep 4.2](https://reproducible-reporting.github.io/stepup-reprep/).

This development release contains the inventory tools and the Zenodo synchronization
of StepUp RepRep 4.2 under new names:

- `make_inventory()` and `sd-make-inventory` record files with their sizes and digests
  in an inventory, a JSON Lines file.
- `zip_inventory()` and `sd-zip-inventory` check the files against an inventory
  and pack them into a reproducible ZIP file.
- `sd-check-inventory` checks files on disk against an inventory.
- `sync_zenodo()` and `sd-sync-zenodo` keep the files of an inventory in sync
  with a draft dataset on Zenodo.
  The token is taken from `STEPUP_DATA_ZENODO_TOKEN`.

The functions are imported from `stepup.data.api` in the `plan.py` of a StepUp workflow.
Inventories, Zenodo configuration files and record-id files
written for StepUp RepRep 4.2 are accepted unchanged.

- Documentation: <https://reproducible-reporting.github.io/stepup-data/>
- Source code: <https://github.com/reproducible-reporting/stepup-data/>
