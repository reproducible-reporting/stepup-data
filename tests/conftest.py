# SPDX-FileCopyrightText: 2024 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Pytest configuration."""

import pytest

from stepup.core.path import Path

pytest.register_assert_rewrite("stepup.data.pytest")

# As a plugin, `stepup.core.pytest` also gets its assertions rewritten.
pytest_plugins = ("stepup.core.pytest",)


@pytest.fixture
def path_tmp(tmpdir: str) -> Path:
    return Path(tmpdir)
