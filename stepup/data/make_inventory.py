# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Create an inventory file.

An inventory describes every individual file, with its size and optionally its digest,
in the format defined in `stepup.data.inventory`.
"""

import argparse
import sys
from collections.abc import Sequence

from stepup.core.api import amend, glob
from stepup.core.nglob import NamedGlob, has_any_wildcards
from stepup.core.path import Path, StrPath
from stepup.core.platform.oscompat import file_modes_available
from stepup.core.stepinfo import StepInfo, load_step_info

from .inventory import (
    HASH_ALGORITHMS,
    InventoryHeader,
    compute_record,
    format_header,
    format_record,
)

__all__ = ("NO_HASH", "main", "write_inventory")


NO_HASH = "none"
"""The value of the option `--hash` that leaves out the digests."""


def main(argv: Sequence[str] | None = None):
    """Main program."""
    parser = argparse.ArgumentParser(
        prog="sd-make-inventory",
        description="Make an inventory file in JSON Lines format. "
        "All paths and patterns are relative to the current directory. "
        "Quote the patterns, so that the shell does not expand them.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files to include in the inventory, in the given order. "
        "They are never interpreted as patterns.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="PATTERN",
        help="A pattern of files to include, or a literal path when it has no wildcards. "
        "The included files come after the positional paths, sorted. "
        "A pattern that matches no files is an error. "
        "This option can be repeated.",
    )
    parser.add_argument(
        "--include-info-inp",
        action="append",
        default=[],
        metavar="INFO",
        help="A step info file, whose input paths are included. "
        "The included files come after the positional paths, sorted. "
        "This option can be repeated.",
    )
    parser.add_argument(
        "--include-info-out",
        action="append",
        default=[],
        metavar="INFO",
        help="A step info file, whose output paths are included. "
        "The included files come after the positional paths, sorted. "
        "This option can be repeated.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="A pattern or a path of files to leave out, "
        "whether they were given as positional paths or with one of the --include options. "
        "It is matched against the names of the selected files, not against the disk. "
        "This option can be repeated.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="The inventory file to write, with suffix .jsonl.",
    )
    parser.add_argument(
        "--hash",
        dest="hash_algorithm",
        choices=[*HASH_ALGORITHMS, NO_HASH],
        default="md5",
        help="The hash algorithm for the digests of the files. "
        f"With {NO_HASH}, no digests are recorded and the contents of the files are not read. "
        "[default=%(default)s]",
    )
    parser.add_argument(
        "--mode",
        default=False,
        action="store_true",
        help="Also record the permission bits of the files.",
    )
    args = parser.parse_args(argv)
    if not (args.paths or args.include or args.include_info_inp or args.include_info_out):
        parser.error(
            "At least one path, --include, --include-info-inp or --include-info-out is needed."
        )
    paths = select_paths(
        args.paths,
        args.include,
        args.exclude,
        args.output,
        include_info_inp=args.include_info_inp,
        include_info_out=args.include_info_out,
    )
    hash_algorithm = None if args.hash_algorithm == NO_HASH else args.hash_algorithm
    write_inventory(args.output, paths, hash_algorithm=hash_algorithm, mode=args.mode)


def select_paths(
    paths: Sequence[StrPath],
    include: Sequence[str],
    exclude: Sequence[str],
    path_out: StrPath,
    *,
    include_info_inp: Sequence[StrPath] = (),
    include_info_out: Sequence[StrPath] = (),
) -> list[Path]:
    """Select the files of an inventory.

    The patterns in `include` are matched with `stepup.core.api.glob()`,
    so that the current step becomes pending when their matches change.
    Like any `glob()` match, a matched file must be static.
    The step info files are amended as inputs of the current step before they are read,
    so that the step reruns when the lists of files in them change.

    Parameters
    ----------
    paths
        Literal paths, which come first, in the given order.
    include
        Patterns, or literal paths when they have no wildcards.
        The matches and the literal paths come after `paths`, sorted.
    exclude
        Patterns or literal paths, matched against the normalized names of the selected files.
        Excluded files are removed, whichever argument selected them.
    path_out
        The inventory to be written, which must not be selected.
    include_info_inp, include_info_out
        Step info files, as written by `stepup.core.stepinfo.dump_step_info()`,
        whose `inp` or `out` paths, respectively, are included.
        These paths are sorted together with those of `include`.

    Returns
    -------
    selected
        The normalized paths of the selected files.
        These may still contain duplicates relative to the directory of the inventory.

    Raises
    ------
    ValueError
        When an include pattern matches no files, or when the inventory itself is selected.
    """
    selected = [Path(path).normpath() for path in paths]
    included = set()
    for entry in include:
        if has_any_wildcards(entry):
            matches = [path for path in glob(entry).files() if not path.endswith("/")]
            if len(matches) == 0:
                raise ValueError(f"The include pattern {entry} matches no files.")
            included.update(path.normpath() for path in matches)
        else:
            included.add(Path(entry).normpath())
    paths_info = sorted({Path(path).normpath() for path in [*include_info_inp, *include_info_out]})
    if len(paths_info) > 0:
        amend(inp=paths_info)
    for path_info in include_info_inp:
        included.update(read_step_info_paths(path_info, "inp"))
    for path_info in include_info_out:
        included.update(read_step_info_paths(path_info, "out"))
    selected.extend(sorted(included))

    excluded = set()
    for pattern in exclude:
        ng = NamedGlob(pattern)
        ng.extend(selected)
        excluded.update(ng.files())
    selected = [path for path in selected if path not in excluded]

    if Path(path_out).normpath() in selected:
        raise ValueError(f"The inventory {path_out} cannot list itself.")
    return selected


def read_step_info_paths(path_info: StrPath, field: str) -> list[Path]:
    """Read the paths of one field of the step infos in a file.

    Parameters
    ----------
    path_info
        A file with one step info or a list of them.
    field
        The field whose paths are read: `inp` or `out`.

    Returns
    -------
    paths
        The normalized paths, relative to the current directory unless absolute.
    """
    if field not in ("inp", "out"):
        raise ValueError(f"Only the fields inp and out can be read, got {field}")
    infos = load_step_info(path_info)
    if isinstance(infos, StepInfo):
        infos = [infos]
    return [path for info in infos for path in getattr(info.rebase("."), field)]


def write_inventory(
    path_out: StrPath,
    paths: Sequence[StrPath],
    *,
    hash_algorithm: str | None = "md5",
    mode: bool = False,
    do_amend: bool = True,
):
    """Write an inventory file.

    Parameters
    ----------
    path_out
        The location of the inventory file to be written, with suffix `.jsonl`.
    paths
        The paths to be included in the inventory, in the order of the records.
        These must be paths relative to the current working directory.
        They will be written to the inventory file
        as paths relative to the parent of the inventory file.
        When two of them are the same after this conversion, only the first one is kept.
    hash_algorithm
        The name of the `hashlib` algorithm that digests the regular files,
        or `None` to record no digests.
    mode
        When True, the permission bits of the regular files are recorded.
        A warning is printed on a platform where files have no permission bits.
    do_amend
        When True, `paths` are amended as inputs of the current step,
        so that the inventory is rebuilt when they change.
        Set this to False when the step already declares these files itself,
        because the extra amendment may then introduce a cyclic dependency.
    """
    path_out = Path(path_out)
    if not path_out.endswith(".jsonl"):
        raise ValueError(f"The inventory file must have a `.jsonl` extension. Got {path_out}")
    header = InventoryHeader(hash_algorithm, mode)
    if mode and not file_modes_available():
        print(
            "WARNING: Files have no permission bits on this platform. "
            "The recorded modes are derived from the read-only attribute and the file name.",
            file=sys.stderr,
        )

    root = path_out.parent.normpath()
    unique_paths = []
    seen = set()
    for path in paths:
        path = Path(path)
        relpath = path.relpath(root).normpath()
        if relpath not in seen:
            seen.add(relpath)
            unique_paths.append(path)

    if do_amend:
        for path in unique_paths:
            if path.endswith("/") or path.is_dir():
                raise ValueError(f"Directories are not allowed in the inventory: {path}")
        amend(inp=unique_paths)

    with open(path_out, "w", encoding="utf-8", newline="\n") as fh:
        print(format_header(header), file=fh)
        for path in unique_paths:
            record = compute_record(path, root, hash_algorithm, mode)
            print(format_record(record, header), file=fh)


if __name__ == "__main__":
    sys.exit(main())
