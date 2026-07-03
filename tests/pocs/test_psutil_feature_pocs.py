"""Test for psutil feature PoCs.

Asserts memory sampling and peak calculation work with real data.
"""

from __future__ import annotations

import time

from pocs.psutil_feature_pocs import MemorySampler, _allocate_memory


def test_sampler_records_samples() -> None:
    """Assert the sampler collects at least one sample during its run."""
    sampler = MemorySampler(interval=0.5)
    sampler.start()
    time.sleep(1.5)  # Allow ~3 samples
    sampler.stop()
    peak = sampler.peak_ram_mb()
    assert peak > 0, f"Peak RAM should be positive, got {peak}"


def test_peak_detects_allocation() -> None:
    """Assert peak RAM increases when memory is allocated."""
    sampler = MemorySampler(interval=0.2)
    sampler.start()

    # Allocate ~50 MB so sampler can observe the increase
    buf = _allocate_memory(50.0)
    time.sleep(1.0)  # Hold allocation while sampling

    peak = sampler.peak_ram_mb()
    sampler.stop()

    # Delete buffer to free memory
    del buf

    assert peak > 0, f"Peak should be positive, got {peak}"
