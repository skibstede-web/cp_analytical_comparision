import nir_cp
from nir_cp.config import (
    DEFAULT_ALPHA_ACCURACY,
    DEFAULT_ALPHA_PRECISION,
    DEFAULT_RANDOM_SEED,
)


def test_project_imports() -> None:
    assert nir_cp is not None


def test_default_config_values() -> None:
    assert DEFAULT_ALPHA_ACCURACY == 0.05
    assert DEFAULT_ALPHA_PRECISION == 0.05
    assert isinstance(DEFAULT_RANDOM_SEED, int)
