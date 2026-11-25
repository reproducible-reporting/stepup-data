---
description: >-
  The inventory.jsonl file format, the selection of the files it lists,
  and the tools that create, validate and zip an inventory of files to be archived.
---

<!--
SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Inventory Files

An inventory lists files together with their sizes and, by default, their digests.
StepUp Data uses inventories to prepare reproducible ZIP archives,
to check the integrity of a dataset, and to upload files to Zenodo with
[`sync_zenodo()`](sync_zenodo.md).
Inventory files can either be created for an external dataset
or within a StepUp workflow, for a dataset that the workflow builds.

## File Formats

### Inventory Files (`inventory.jsonl`)

An inventory is a [JSON Lines](https://jsonlines.org/) file
with one JSON object per line, encoded in UTF-8.
You do not write this type of file by hand.
Instead, StepUp Data offers tools to make such files, see below.
The following example lists a regular file and a symbolic link:

```json
{"fields":["md5","path","size"],"format":"stepup-inventory","version":1}
{"md5":"b1946ac92492d2347c6235b4d2611184","path":"README.txt","size":6}
{"link":"README.txt","path":"README.md"}
```

The first line is the header, with the following keys:

- `format` is always `"stepup-inventory"`,
  which tells an inventory apart from other JSON files.
- `version` is the version of the format, currently `1`.
  It changes with every incompatible change of the format.
- `fields` is the sorted list of keys of the line of a regular file.

Every other line describes one file.
For a regular file, the keys are exactly those listed in `fields`:

- `path` is the location of the file, see below.
- `size` is the size of the file in bytes.
- The digest of the file contents in lowercase hexadecimal digits,
  under the name of the hash algorithm, e.g. `md5` or `sha256`.
  All files in one inventory are hashed with the same algorithm.
  The digest is absent when the inventory was made with `--hash none`.
- `mode` is only present when the inventory was made with `--mode`.
  It holds the permission bits of the file, e.g. `rw-r--r--`.

A symbolic link is never followed.
Its line has exactly two keys, whatever `fields` says:
`path` is the location of the link, and `link` is the target as stored in the link.

A path is relative to the parent directory of the inventory file,
it is normalized and it uses `/` as separator on every platform.
It may start with `../` for a file outside that directory.
Directories are never listed, and neither are symbolic links to directories,
because StepUp cannot track a directory as an input.
`sd-make-inventory` refuses them when they are given by name,
and leaves them out when an include pattern matches them.

Files appear in the order in which they were given:
first the paths given by name, in the given order,
then the included files, sorted.
When a path occurs twice, only its first occurrence is kept.

The contents of an inventory only depend on the files it lists.
It contains no time stamps, so StepUp does not rerun the steps that use it
when the files did not change.

## Selecting Files

The files of an inventory are selected in a fixed order:

1. The paths given by name, which are always literal paths, never patterns.
   These are the argument `paths` of `make_inventory()`,
   or the positional arguments of `sd-make-inventory`.
2. The files selected with `include`.
   An entry with wildcards is a
   [Named Glob pattern](https://reproducible-reporting.github.io/stepup-core/reference/stepup.core.nglob/),
   which may also contain `**` wildcards to match files recursively.
   An entry without wildcards is a literal path.
3. The inputs or outputs listed in step info files,
   see [Files Listed in Step Info Files](#files-listed-in-step-info-files) below.
4. Every file that matches an `exclude` pattern or path is removed,
   whichever of the above selected it.

The order of the arguments does not matter,
so a file that was excluded cannot be included again.
All paths and patterns are relative to the working directory of the step,
or to the current directory on the command line.

The include patterns follow the rules of
[`glob()`](https://reproducible-reporting.github.io/stepup-core/reference/stepup.core.api/#stepup.core.api.glob)
in StepUp Core:

- A pattern only matches static files,
  e.g. those inside a directory declared with `static("data/")`.
  A file that a step builds must be listed by name,
  in `paths` or as an include entry without wildcards.
  A pattern that matches a built file fails the build.
- When the set of files matched by a pattern changes, the inventory is rebuilt.
- A pattern that matches no files is an error, to catch typos.
  Directories matched by a pattern are left out.

An exclude is matched against the normalized paths of the selected files, not against the disk,
so it is not an error when it matches nothing.
The inventory itself cannot be selected.

On the command line, quote the patterns,
so that the shell passes them to `sd-make-inventory` unchanged.
For example, Bash without the `globstar` option expands an unquoted `data/**` like `data/*`,
which then silently matches only one level of the directory tree.

### Files Listed in Step Info Files

An inventory can include the inputs or outputs listed in step info files,
see [`StepInfo` Objects][core-step-info] in the documentation of StepUp Core.
This is convenient for files built by other steps,
because those cannot be matched by an include pattern.
Any tool can write a step info file for StepUp Data to read,
following the format described in [Step Info Files][core-step-info-files].

The following `plan.py` makes an inventory of the inputs and outputs of the steps
planned by `work/generate.py`:

```python
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
```

The argument `include_info_inp` adds the `inp` paths of the steps in the step info files,
and `include_info_out` adds their `out` paths.
On the command line, these are the options `--include-info-inp` and `--include-info-out`.
Pass a file to both arguments to include the inputs as well as the outputs,
or choose one, depending on the purpose of the inventory:

- The outputs are the dataset produced by the steps, e.g. to archive their results.
- The inputs are the data the steps consumed, e.g. to archive what is needed to reproduce them.

Volatile files are never included, because they change at every run.
In the example above, the script itself is an input of the steps it plans,
which `exclude="**/*.py"` removes from the inventory.

The step info files are inputs of the inventory step,
so the inventory is made after the step that writes them.

[core-step-info]: https://reproducible-reporting.github.io/stepup-core/tutorials/step_info/
[core-step-info-files]: https://reproducible-reporting.github.io/stepup-core/tutorials/step_info/#step-info-files

## Creating `inventory.jsonl` Files

### Command-Line Tool `sd-make-inventory`

One can create an inventory file on the command-line as follows:

```bash
sd-make-inventory README.txt --include 'data/**' --exclude '**/*.log' -o inventory.jsonl
```

The output, given with `-o`, is required and must have the suffix `.jsonl`.
The options `--include`, `--include-info-inp`, `--include-info-out` and `--exclude`
can be repeated,
and at least one positional path or one of the `--include` options is needed.
See `sd-make-inventory --help` for more details.
This tool is suitable for creating inventory files of external datasets.

### StepUp Data Function `make_inventory`

One may include a [`make_inventory()`][stepup.data.api.make_inventory] step in `plan.py` as follows:

```python
from stepup.data.api import make_inventory

make_inventory("inventory.jsonl", paths=["file1.txt", "file2.txt"])
```

The first argument is the inventory file to write.
All other arguments are keyword-only.
This step is mainly useful for creating an inventory file of a dataset generated by your StepUp workflow.
Files can also be selected with the arguments `include` and `exclude`,
each of which takes a string or a list of strings, like `paths`:

```python
from stepup.core.api import static
from stepup.data.api import make_inventory

static("data/")
make_inventory(
    "inventory.jsonl",
    paths="results/table.csv",
    include=["results/figure.pdf", "data/**"],
    exclude="**/*.log",
)
```

Here, `results/table.csv` and `results/figure.pdf` may be built by other steps,
because they are listed by name,
while the pattern `data/**` matches the static files in `data/`.

The options below are the arguments `hash_algorithm` and `mode` of `make_inventory()`.

### Hash Algorithm

The option `--hash` selects the hash algorithm for the digests of the files.
Any algorithm in Python's
[`hashlib.algorithms_guaranteed`](https://docs.python.org/3/library/hashlib.html#hashlib.algorithms_guaranteed)
can be used, except the `shake_*` algorithms, whose digests have no fixed length.

The default is MD5, because Zenodo reports MD5 checksums.
MD5 reliably detects accidental changes, such as a damaged transfer or bit rot,
because the chance of an accidental collision is negligible with MD5 as well as with SHA-256.
Use `--hash sha256` when deliberate tampering with the files must be detected,
because files with the same MD5 digest can be crafted on purpose.

With `--hash none`, or `hash_algorithm=None` in `make_inventory()`, no digests are recorded.
The contents of the files are then never read,
which saves a lot of time for large datasets or files on network storage.
The price is that only the sizes, the permission bits and the link targets are checked,
so a change that keeps the size of a file goes unnoticed.
Such an inventory cannot be used with `sync_zenodo()`, which needs MD5 checksums.

### Permission Bits

The size of a regular file is always recorded, and so is its digest unless `--hash none` is given.
The permission bits are only recorded with the option `--mode`,
e.g. to make sure that a script remains executable.
They are then also checked by `sd-check-inventory` and `sd-zip-inventory`.

Files have no permission bits on Windows,
where Python derives them from the read-only attribute and the file name.
`sd-make-inventory --mode` prints a warning on Windows,
and the permission bits in an inventory are not checked on Windows.

## Creating a ZIP Archive from an `inventory.jsonl` File

### Command-Line Tool `sd-zip-inventory`

Given an `inventory.jsonl` file, the corresponding ZIP file is created with:

```bash
sd-zip-inventory inventory.jsonl
```

This is a command-line wrapper around the `zip_inventory` function discussed below.

### StepUp Data Function `zip_inventory`

The function [`zip_inventory()`][stepup.data.api.zip_inventory]
takes an `inventory.jsonl` file as input
and creates a ZIP file containing all the files listed in the inventory.
By default, the ZIP file is written next to the inventory, e.g. `inventory.zip`.
Its second argument is a file or a directory with a trailing slash for the ZIP file.
It differs from the conventional `zip` program in the following ways:

- Every file is checked against the inventory before it is added to the archive,
  which is mostly useful for external datasets.
  An inventory without digests can be zipped too,
  but then only the sizes, permission bits and link targets are checked.
- The listed files are inputs of the step, besides the inventory,
  so the ZIP file is rebuilt whenever one of them changes,
  even when the inventory itself stays the same.
- The inventory itself is not added to the ZIP file.
- The paths in the ZIP file are those in the inventory.
  A file outside the directory of the inventory, with a path starting with `../`,
  cannot be archived, so such an inventory is refused.
- The ZIP file is reproducible: all time stamps in the ZIP file are set to January 1st, 1980.
- Symbolic links are added as links, instead of the contents they point to.

For archival, keep the inventory as a separate file next to the ZIP file,
e.g. by uploading both to Zenodo,
so that the unpacked files can be checked with `sd-check-inventory`.

### Unpacking the ZIP File

To unpack the ZIP file, use the following command:

```bash
unzip inventory.zip
```

This will correctly handle symbolic links, unlike Python's built-in
[extractall](https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.extractall) method.
See [cpython#82102](https://github.com/python/cpython/issues/82102)
for more details on Python's (lacking) support for symbolic links in ZIP files.

The paths in the ZIP file are relative to the directory of the inventory.
Unpack the ZIP file in the directory that contains its inventory,
so that the unpacked files can be checked with `sd-check-inventory`, see below.

## Validate an Inventory File

If you just want to check the files listed in an inventory, run:

```bash
sd-check-inventory inventory.jsonl
```

This compares the size of every regular file,
its digest and its permission bits when the inventory has them,
and the target of every symbolic link.
This can be useful in the following cases:

- When you work with a remote dataset, you can check if the files in the inventory have changed.
- When you unpack a ZIP file created by `sd-zip-inventory` or `zip_inventory()`
  next to its inventory,
  you can check if the files are not affected by bit rot or other data integrity issues.
