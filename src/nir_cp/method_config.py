"""Method-specific configuration loading for CP method modules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REQUIRED_METHOD_KEYS = ("granule_assay_nir", "tablet_transmission_nir")
REQUIRED_FIELDS = (
    "method_display_name",
    "d_equivalence_margin",
    "k_precision_ratio",
    "alpha_accuracy",
    "alpha_precision",
    "recommended_min_n",
    "notes",
)


def _validate_method_fields(method_key: str, config: dict[str, Any]) -> None:
    missing_fields = sorted(set(REQUIRED_FIELDS) - set(config))
    if missing_fields:
        raise ValueError(f"{method_key} is missing required fields: {missing_fields}")


def load_method_defaults(path: str | Path = "config/method_defaults.yaml") -> dict[str, Any]:
    """Load and validate method default configuration from YAML."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(config_path)

    with config_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)

    if not isinstance(loaded, dict):
        raise ValueError("Method defaults YAML must contain a mapping.")

    missing_methods = sorted(set(REQUIRED_METHOD_KEYS) - set(loaded))
    if missing_methods:
        raise ValueError(f"Missing required method keys: {missing_methods}")

    for method_key in REQUIRED_METHOD_KEYS:
        method_config = loaded[method_key]
        if not isinstance(method_config, dict):
            raise ValueError(f"{method_key} must contain a mapping of defaults.")
        _validate_method_fields(method_key, method_config)

    return loaded


def get_method_config(
    method_key: str,
    path: str | Path = "config/method_defaults.yaml",
) -> dict[str, Any]:
    """Return validated configuration for one method key."""

    defaults = load_method_defaults(path)
    if method_key not in defaults:
        raise KeyError(f"Method not found: {method_key}")

    method_config = defaults[method_key]
    _validate_method_fields(method_key, method_config)
    return method_config


def list_available_methods(path: str | Path = "config/method_defaults.yaml") -> list[str]:
    """Return available method configuration keys."""

    return list(load_method_defaults(path).keys())
