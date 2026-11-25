# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Run examples."""

import os

import pytest

from stepup.core.path import Path
from stepup.core.pytest import EXAMPLE_TIMEOUT
from stepup.data.pytest import run_example

pytestmark = pytest.mark.timeout(2 * EXAMPLE_TIMEOUT)
"""Budget for a whole example, which `run_example` already bounds with `EXAMPLE_TIMEOUT`.

Setup, call and teardown share this budget,
and it must stay above the deadline of the example itself,
so that a stalled example is reported with its own output instead of a bare timeout.
"""

OVERWRITE_EXPECTED = "STEPUP_OVERWRITE_EXPECTED" in os.environ


@pytest.mark.parametrize(
    "name",
    [
        "inventory_built",
        "inventory_glob_built",
        "inventory_step_info",
        "make_inventory_list",
        "sync_zenodo",
        "zip_inventory",
        "zip_patterns",
        "zip_tree",
    ],
)
@pytest.mark.asyncio
async def test_example(path_tmp, name: str):
    await run_example(Path("tests/examples") / name, path_tmp, OVERWRITE_EXPECTED)
