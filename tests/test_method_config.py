from pathlib import Path

import pytest

from nir_cp.method_config import (
    REQUIRED_FIELDS,
    get_method_config,
    list_available_methods,
    load_method_defaults,
)


CONFIG_PATH = Path("config/method_defaults.yaml")


def test_load_method_defaults_loads_config() -> None:
    defaults = load_method_defaults(CONFIG_PATH)

    assert isinstance(defaults, dict)
    assert defaults["granule_assay_nir"]["d_equivalence_margin"] == 1.0


def test_both_method_keys_exist() -> None:
    methods = list_available_methods(CONFIG_PATH)

    assert "granule_assay_nir" in methods
    assert "tablet_transmission_nir" in methods


def test_required_fields_exist_for_each_method() -> None:
    defaults = load_method_defaults(CONFIG_PATH)

    for method_key in ("granule_assay_nir", "tablet_transmission_nir"):
        assert set(REQUIRED_FIELDS).issubset(defaults[method_key])


def test_get_method_config_returns_method_specific_dict() -> None:
    config = get_method_config("tablet_transmission_nir", CONFIG_PATH)

    assert config["method_display_name"] == "Off-line Tablet Transmission NIR"
    assert config["recommended_min_n"] == 24


def test_missing_method_raises_key_error() -> None:
    with pytest.raises(KeyError, match="Method not found"):
        get_method_config("missing_method", CONFIG_PATH)
