"""Test for psutil library PoC.

Asserts the PoC produces valid output (positive RAM measurement).
"""

from __future__ import annotations

from pocs.psutil_library_poc import get_process_ram_mb


def test_ram_measurement_positive() -> None:
    """Assert psutil returns a positive RAM value for the current process."""
    ram_mb = get_process_ram_mb()
    assert ram_mb > 0, f"RAM should be positive, got {ram_mb}"
    assert isinstance(ram_mb, float), "RAM should be a float"
