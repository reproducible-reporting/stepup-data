# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Application programming interface for StepUp Data."""

from collections.abc import Collection

from stepup.core.api import run, shq
from stepup.core.nglob import has_any_wildcards
from stepup.core.path import StrPath, coerce_paths, coerce_str, make_path_out
from stepup.core.stepinfo import StepInfo

from .make_inventory import NO_HASH

__all__ = ("make_inventory", "sync_zenodo", "zip_inventory")


def make_inventory(
    dest: StrPath,
    *,
    paths: StrPath | Collection[StrPath] = (),
    include: str | Collection[str] = (),
    include_info_inp: StrPath | Collection[StrPath] = (),
    include_info_out: StrPath | Collection[StrPath] = (),
    exclude: str | Collection[str] = (),
    hash_algorithm: str | None = "md5",
    mode: bool = False,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Create an inventory file, in JSON Lines format with suffix `.jsonl`.

    The format and the selection of the files are explained in the documentation of StepUp Data,
    under "Inventory Files".
    All paths and patterns are relative to the working directory of the step.

    Parameters
    ----------
    dest
        The inventory file to write, with suffix `.jsonl`.
    paths
        Files to include in the inventory, in the given order.
        They are never interpreted as patterns.
    include
        Patterns of files to include, which must match static files.
        An entry without wildcards is a literal path,
        which may also be the output of another step.
        The included files come after `paths`, sorted.
        A pattern that matches no files is an error.
    include_info_inp, include_info_out
        Step info files, whose `inp` or `out` paths, respectively, are included,
        e.g. written by `dump_step_info()` in StepUp Core.
        The step info files are inputs of the step, and may be built by other steps.
        The included files come after `paths`, sorted together with those of `include`.
    exclude
        Patterns or literal paths of files to leave out,
        matched against the names of the files selected by the other arguments.
    hash_algorithm
        The name of the `hashlib` algorithm for the digests of the files.
        The default, `md5`, is the one that Zenodo reports.
        Use `sha256` when deliberate tampering with the files must be detected.
        With `None`, no digests are recorded and the contents of the files are not read,
        which saves time for large datasets,
        but then changes that keep the size of a file are not detected,
        and the inventory cannot be used by `sync_zenodo()`.
    mode
        When True, the permission bits of the files are recorded and checked.
        Files have no permission bits on Windows,
        where the recorded modes depend on the read-only attribute and the file names.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    if not coerce_str(dest).endswith(".jsonl"):
        raise ValueError(f"The inventory file must have a `.jsonl` extension. Got {dest}")
    paths_inp = coerce_paths(paths)
    include = [include] if isinstance(include, str) else list(include)
    include_info_inp = coerce_paths(include_info_inp)
    include_info_out = coerce_paths(include_info_out)
    exclude = [exclude] if isinstance(exclude, str) else list(exclude)
    if not (paths_inp or include or include_info_inp or include_info_out):
        raise ValueError("At least one path, include entry or step info file must be given.")
    parts = ["sd-make-inventory"]
    if len(paths_inp) > 0:
        parts.append(shq(paths_inp))
    parts.extend(f"--include {shq(entry)}" for entry in include)
    parts.extend(f"--include-info-inp {shq(path)}" for path in include_info_inp)
    parts.extend(f"--include-info-out {shq(path)}" for path in include_info_out)
    parts.extend(f"--exclude {shq(entry)}" for entry in exclude)
    parts.append(f"-o {shq(dest)}")
    if hash_algorithm is None:
        parts.append(f"--hash {NO_HASH}")
    elif hash_algorithm != "md5":
        parts.append(f"--hash {shq(hash_algorithm)}")
    if mode:
        parts.append("--mode")
    # Literal includes and step info files are declared,
    # so that the step waits for them when another step builds them.
    paths_inp.extend(entry for entry in include if not has_any_wildcards(entry))
    paths_inp.extend(include_info_inp + include_info_out)
    return run(
        " ".join(parts),
        inp=paths_inp,
        out=[dest],
        optional=optional,
        resources=resources,
        duration=duration,
    )


def zip_inventory(
    path_inventory: StrPath,
    dest: StrPath | None = None,
    *,
    optional: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Create a ZIP file with all files listed in an inventory, after checking them.

    Parameters
    ----------
    path_inventory
        An inventory file with suffix `.jsonl`,
        created with `make_inventory()` or with the command-line script `sd-make-inventory`.
        The files are stored in the ZIP file under the paths of their records,
        which must therefore be inside the directory of the inventory.
        They are also amended as inputs of the step,
        so the ZIP file is rebuilt when they change, even when the inventory does not.
        The inventory itself is not added to the ZIP file.
        Keep the inventory next to the ZIP file
        to check the unpacked files with `sd-check-inventory`.
    dest
        Output destination: `None`, a directory with a trailing slash, or a file.
        When `None`, the ZIP file is written next to the inventory, with suffix `.zip`.
        In a directory, the ZIP file has the name of the inventory, with suffix `.zip`.
        A file must have suffix `.zip`.
    optional
        If `True`, the step is only executed when needed by other steps.
    resources
        Named resources required to run this step, e.g. `{"gpu": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    if not coerce_str(path_inventory).endswith(".jsonl"):
        raise ValueError(f"The inventory file must have a `.jsonl` extension. Got {path_inventory}")
    path_zip = make_path_out(path_inventory, dest, ".zip")
    return run(
        f"sd-zip-inventory {shq(path_inventory)} {shq(path_zip)}",
        inp=path_inventory,
        out=path_zip,
        optional=optional,
        resources=resources,
        duration=duration,
    )


def sync_zenodo(
    path_config: StrPath,
    path_description: StrPath,
    path_inventory: StrPath,
    *,
    check_md5: bool = False,
    verbose: bool = False,
    resources: dict[str, int] | str | None = None,
    duration: float | None = None,
) -> StepInfo:
    """Synchronize data with a draft dataset on Zenodo.

    The step runs at every start of StepUp, after every change of its inputs,
    and in watch mode after the `R` key or `stepup rebuild --recheck`,
    as a step with `recheck=True` in StepUp Core.
    It contacts Zenodo only when the `STEPUP_DATA_ZENODO_TOKEN` environment variable is set
    and StepUp does not run offline.

    Parameters
    ----------
    path_config
        The configuration file for the Zenodo upload, in YAML, JSON or TOML format.
    path_description
        A Markdown (`.md`) or HTML (`.html`) file with the description of the dataset.
        Markdown is converted to HTML before it is sent to Zenodo.
    path_inventory
        The inventory of the files to upload, usually written by `make_inventory()`
        with the default hash algorithm, MD5.
        The paths in the inventory are relative to its parent directory.
        Zenodo does not support directory layouts or symbolic links,
        so all files must be regular files with different names.
        At most 100 files can be uploaded to a single record.
        The first file is selected for preview on Zenodo.
    check_md5
        When True, the MD5 checksums of the local files are computed again
        and compared to those in the inventory before anything is uploaded.
        This suits an inventory that is not built in the same workflow.
        An inventory built by `make_inventory()` is always up to date,
        so the check is then redundant.
    verbose
        Set to True to print Zenodo API requests and responses to the standard output.
    resources
        Named resources required to run this step, e.g. `{"zenodo": 1}`.
        See `stepup.core.api.step()` for details.
    duration
        An initial estimate of the step's wall time in seconds.
        See `stepup.core.api.step()` for details.

    Returns
    -------
    step_info
        Holds relevant information of the step, useful for defining follow-up steps.
    """
    parts = [
        "sd-sync-zenodo",
        shq(path_config),
        shq(path_description),
        shq(path_inventory),
    ]
    if not check_md5:
        parts.append("--no-check-md5")
    if verbose:
        parts.append("--verbose")
    return run(
        " ".join(parts),
        inp=[path_config, path_description, path_inventory],
        recheck=True,
        resources=resources,
        duration=duration,
    )
