# SPDX-FileCopyrightText: 2026 Toon Verstraelen <Toon.Verstraelen@UGent.be>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""The `STEPUP_DATA_*` environment variables of StepUp Data.

They are registered with StepUp Core through the `stepup.env_vars` entry point,
so that `stepup config` lists them and masks the secret ones.
"""

from stepup.core.env_vars import EnvVarInfo, EnvVarRegistry

__all__ = ("env_vars",)


def env_vars() -> EnvVarRegistry:
    """Return the environment variables of StepUp Data."""
    return EnvVarRegistry(
        "StepUp Data",
        {"STEPUP_DATA_ZENODO_TOKEN": EnvVarInfo(secret=True)},
    )
