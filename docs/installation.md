---
description: >-
  Install StepUp Data from PyPI or conda-forge, with pip, uv, pixi or conda,
  on Linux, macOS or Windows,
  which also installs StepUp Core,
  and find out which functions are tested on Windows.
---

<!--
SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Installation

## Requirements

- Linux, macOS or Windows.
  [Supported Platforms][core-platforms] in the documentation of StepUp Core
  explains what differs between them.
  [Windows](#windows) below adds what is specific to StepUp Data.
- [Python](https://www.python.org/) ≥ 3.11.
  On Windows, StepUp Core recommends a minimal patch release for security reasons,
  see its [installation instructions][core-installation].
- A package manager, such as [pip](https://pip.pypa.io/), [uv](https://docs.astral.sh/uv/),
  [pixi](https://pixi.prefix.dev/) or [conda](https://docs.conda.io/).

StepUp Data is published on both [PyPI](https://pypi.org/)
and [conda-forge](https://conda-forge.org/), under the same package name `stepup-data`.
Both also install StepUp Core as a dependency.

We recommend installing into an isolated environment,
such as a [Python virtual environment](https://docs.python.org/3/library/venv.html)
or a pixi workspace,
and activating it with [direnv](https://direnv.net/).

## Installing from PyPI

Use one of the following commands:

```bash
pip install stepup-data     # in an activated virtual environment
uv pip install stepup-data  # same, with uv
uv add stepup-data          # in a uv project
```

## Installing from conda-forge

Use one of the following commands:

```bash
pixi add stepup-data                      # in a pixi workspace
conda install -c conda-forge stepup-data  # in an activated conda environment
```

## Windows

StepUp Data runs natively on Windows, without WSL.
The [Windows section of Supported Platforms][core-windows]
explains what a workflow has to take care of on Windows,
e.g. how to put a path into a command.
The rest of this section is specific to StepUp Data.

### Tested Functions

The test suite runs on Windows for the following functions of `stepup.data.api`:

- [`make_inventory()`][stepup.data.api.make_inventory]
- [`zip_inventory()`][stepup.data.api.zip_inventory]

### Text Files

All tools of StepUp Data read text files as UTF-8,
and write them as UTF-8 with `\n` line endings, on every platform.

### Inventories and ZIP Files

Windows has no permission bits.
An inventory only records the permission bits of files when it is made with `--mode`,
see [Inventory Files](tutorials/inventory_files.md#permission-bits).
An inventory made on Windows with `--mode` records other permission bits
than one made of the same files on Linux or macOS,
e.g. `rw-rw-rw-` instead of `rw-r--r--`,
and `sd-make-inventory` then prints a warning.
Symbolic links have no recorded permission bits, only their target.
[`zip_inventory()`][stepup.data.api.zip_inventory] stores the file modes on disk in the ZIP file,
so a ZIP file made on Windows also differs from one made on Linux or macOS.

`sd-check-inventory` and `sd-zip-inventory` only compare permission bits on Linux and macOS.
An inventory made on Linux or macOS can be checked on Windows,
but one made on Windows with `--mode` fails the check on Linux and macOS
as soon as the permission bits of a file differ.

[core-platforms]: https://reproducible-reporting.github.io/stepup-core/platforms/
[core-windows]: https://reproducible-reporting.github.io/stepup-core/platforms/#windows
[core-installation]: https://reproducible-reporting.github.io/stepup-core/installation/
