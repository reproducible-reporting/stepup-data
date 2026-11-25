# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for stepup.data.api."""

import inspect

import pytest

from stepup.core.path import PathError
from stepup.data import api
from stepup.data.api import make_inventory, sync_zenodo, zip_inventory


@pytest.fixture
def run_calls(monkeypatch) -> list[tuple[str, dict]]:
    """Replace `run()` in the API module by a function that records the commands and arguments."""
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return command

    monkeypatch.setattr("stepup.data.api.run", fake_run)
    return calls


@pytest.mark.parametrize("name", api.__all__)
def test_keyword_only_options(name: str):
    signature = inspect.signature(getattr(api, name))
    for option in "optional", "resources", "duration":
        parameter = signature.parameters.get(option)
        if parameter is not None:
            assert parameter.kind == inspect.Parameter.KEYWORD_ONLY


def test_make_inventory(run_calls: list[tuple[str, dict]]):
    """The paths keep their order, and the defaults add no options."""
    make_inventory("inventory.jsonl", paths=["b.txt", "a.txt"])
    assert run_calls == [
        (
            "sd-make-inventory b.txt a.txt -o inventory.jsonl",
            {
                "inp": ["b.txt", "a.txt"],
                "out": ["inventory.jsonl"],
                "optional": False,
                "resources": None,
                "duration": None,
            },
        ),
    ]


def test_make_inventory_include_exclude(run_calls: list[tuple[str, dict]]):
    """Literal includes are declared as inputs, unlike patterns and excludes."""
    make_inventory(
        "inventory.jsonl",
        paths="a.txt",
        include=["out/b.txt", "data/**"],
        exclude=["**/*.log", "data/c.txt"],
    )
    assert run_calls == [
        (
            "sd-make-inventory a.txt --include out/b.txt --include 'data/**' "
            "--exclude '**/*.log' --exclude data/c.txt -o inventory.jsonl",
            {
                "inp": ["a.txt", "out/b.txt"],
                "out": ["inventory.jsonl"],
                "optional": False,
                "resources": None,
                "duration": None,
            },
        ),
    ]


def test_make_inventory_strings(run_calls: list[tuple[str, dict]]):
    """A single string is accepted for all arguments that select files."""
    make_inventory("inventory.jsonl", include="data/*.txt", exclude="data/x.txt")
    make_inventory("inventory.jsonl", include_info_out="info.json")
    make_inventory("inventory.jsonl", paths="a.txt")
    assert [command for command, _ in run_calls] == [
        "sd-make-inventory --include 'data/*.txt' --exclude data/x.txt -o inventory.jsonl",
        "sd-make-inventory --include-info-out info.json -o inventory.jsonl",
        "sd-make-inventory a.txt -o inventory.jsonl",
    ]
    assert run_calls[0][1]["inp"] == []
    assert run_calls[1][1]["inp"] == ["info.json"]
    assert run_calls[2][1]["inp"] == ["a.txt"]


def test_make_inventory_step_info(run_calls: list[tuple[str, dict]]):
    """Step info files are declared as inputs, and their options come before the excludes."""
    make_inventory(
        "inventory.jsonl",
        paths="a.txt",
        include="data/*.txt",
        include_info_inp=["one.json", "two.json"],
        include_info_out="one.json",
        exclude="**/*.py",
    )
    assert run_calls == [
        (
            "sd-make-inventory a.txt --include 'data/*.txt' "
            "--include-info-inp one.json --include-info-inp two.json "
            "--include-info-out one.json --exclude '**/*.py' -o inventory.jsonl",
            {
                "inp": ["a.txt", "one.json", "two.json", "one.json"],
                "out": ["inventory.jsonl"],
                "optional": False,
                "resources": None,
                "duration": None,
            },
        ),
    ]


def test_make_inventory_options(run_calls: list[tuple[str, dict]]):
    make_inventory("inventory.jsonl", paths="a.txt", hash_algorithm="sha256", mode=True)
    assert [command for command, _ in run_calls] == [
        "sd-make-inventory a.txt -o inventory.jsonl --hash sha256 --mode",
    ]


def test_make_inventory_no_hash(run_calls: list[tuple[str, dict]]):
    make_inventory("inventory.jsonl", paths="a.txt", hash_algorithm=None)
    assert [command for command, _ in run_calls] == [
        "sd-make-inventory a.txt -o inventory.jsonl --hash none",
    ]


def test_make_inventory_no_paths(run_calls: list[tuple[str, dict]]):
    with pytest.raises(TypeError):
        make_inventory()
    with pytest.raises(ValueError, match="At least one path, include entry or step info file"):
        make_inventory("inventory.jsonl", exclude="*.txt")
    assert run_calls == []


def test_make_inventory_suffix(run_calls: list[tuple[str, dict]]):
    with pytest.raises(ValueError, match=r"\.jsonl"):
        make_inventory("inventory.json", paths="a.txt")
    assert run_calls == []


def test_make_inventory_reprep_calls(run_calls: list[tuple[str, dict]]):
    """Calls written for StepUp RepRep 4.2 fail instead of being misread."""
    with pytest.raises(TypeError):
        make_inventory("a.txt", "inventory.jsonl")
    with pytest.raises(ValueError, match=r"\.jsonl"):
        make_inventory("a.txt")
    assert run_calls == []


@pytest.mark.parametrize(
    ("dest", "path_zip"),
    [(None, "sub/inventory.zip"), ("dist/", "dist/inventory.zip"), ("upload.zip", "upload.zip")],
)
def test_zip_inventory_dest(run_calls: list[tuple[str, dict]], dest: str | None, path_zip: str):
    zip_inventory("sub/inventory.jsonl", dest)
    assert run_calls == [
        (
            f"sd-zip-inventory sub/inventory.jsonl {path_zip}",
            {
                "inp": "sub/inventory.jsonl",
                "out": path_zip,
                "optional": False,
                "resources": None,
                "duration": None,
            },
        ),
    ]


def test_zip_inventory_suffix(run_calls: list[tuple[str, dict]]):
    with pytest.raises(ValueError, match=r"\.jsonl"):
        zip_inventory("inventory.json")
    with pytest.raises(PathError):
        zip_inventory("inventory.jsonl", "upload.tar")
    assert run_calls == []


def test_sync_zenodo(run_calls: list[tuple[str, dict]]):
    """The sync step runs at every start and trusts the inventory built in the workflow."""
    result = sync_zenodo(
        "sync_zenodo.yaml",
        "zenodo_description.md",
        "zenodo_inventory.jsonl",
        resources={"zenodo": 1},
        duration=60.0,
    )
    assert run_calls == [
        (
            "sd-sync-zenodo sync_zenodo.yaml zenodo_description.md zenodo_inventory.jsonl "
            "--no-check-md5",
            {
                "inp": ["sync_zenodo.yaml", "zenodo_description.md", "zenodo_inventory.jsonl"],
                "recheck": True,
                "resources": {"zenodo": 1},
                "duration": 60.0,
            },
        ),
    ]
    assert result == run_calls[0][0]


def test_sync_zenodo_minimal(run_calls: list[tuple[str, dict]]):
    sync_zenodo("sub/other.toml", "sub/other.html", "sub/files.jsonl")
    assert run_calls == [
        (
            "sd-sync-zenodo sub/other.toml sub/other.html sub/files.jsonl --no-check-md5",
            {
                "inp": ["sub/other.toml", "sub/other.html", "sub/files.jsonl"],
                "recheck": True,
                "resources": None,
                "duration": None,
            },
        ),
    ]


def test_sync_zenodo_check_md5(run_calls: list[tuple[str, dict]]):
    sync_zenodo(
        "sync_zenodo.yaml",
        "zenodo_description.md",
        "zenodo_inventory.jsonl",
        check_md5=True,
        verbose=True,
    )
    assert [command for command, _ in run_calls] == [
        "sd-sync-zenodo sync_zenodo.yaml zenodo_description.md zenodo_inventory.jsonl --verbose",
    ]


def test_sync_zenodo_inventory_required(run_calls: list[tuple[str, dict]]):
    with pytest.raises(TypeError):
        sync_zenodo("sync_zenodo.yaml", "zenodo_description.md")
    assert run_calls == []
