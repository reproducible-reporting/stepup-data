# SPDX-FileCopyrightText: 2026 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Tests for stepup.data.env_vars."""

import ast
import os
import re
import subprocess
import sys

import stepup.data
from stepup.core.cli.env_vars_loader import core_env_vars
from stepup.core.path import Path
from stepup.data.env_vars import env_vars


def _string_constants(source: str) -> set[str]:
    """Return every string literal in a module that has the form of a StepUp variable name."""
    return {
        node.value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and re.fullmatch("STEPUP_[A-Z0-9_]+", node.value)
    }


def test_env_vars_are_registered():
    """Every variable that StepUp Data reads is registered, and vice versa.

    A variable that is read but not registered would be listed by `stepup config`
    as being without effect.
    """
    path_package = Path(stepup.data.__file__).parent
    found = set()
    for path in path_package.walkfiles("*.py"):
        if path.name != "env_vars.py":
            found.update(_string_constants(path.read_text(encoding="utf-8")))
    registered = set(env_vars().env_vars)
    assert found - registered <= set(core_env_vars().env_vars)
    assert registered - found == set()


def test_registry():
    registry = env_vars()
    assert registry.package == "StepUp Data"
    for name, info in registry.env_vars.items():
        assert name.startswith("STEPUP_DATA_")
        assert not info.overridden
    assert registry.env_vars["STEPUP_DATA_ZENODO_TOKEN"].secret


def _stepup_config(path_tmp: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    """Run `stepup config` in an environment with no other StepUp variables than those given.

    The home directory is replaced, so that a config file of the developer cannot interfere.
    """
    full_env = {name: value for name, value in os.environ.items() if not name.startswith("STEPUP_")}
    full_env.update(HOME=path_tmp, STEPUP_ROOT=path_tmp, **env)
    return subprocess.run(
        [sys.executable, "-m", "stepup.core", "config"],
        cwd=path_tmp,
        env=full_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_stepup_config_masks_token(path_tmp: Path):
    token = "fake-token-1234567890"
    cp = _stepup_config(path_tmp, {"STEPUP_DATA_ZENODO_TOKEN": token})
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert "# StepUp Data environment variables:\n#   STEPUP_DATA_ZENODO_TOKEN = " in cp.stdout
    assert token not in cp.stdout + cp.stderr
    assert "without effect" not in cp.stdout
    assert "ERROR" not in cp.stdout
