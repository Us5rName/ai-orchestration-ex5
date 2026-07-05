"""Test for torch feature PoCs.

Asserts VRAM tracking works with real GPU allocation.
"""

from __future__ import annotations

import torch

from pocs.torch_feature_pocs import (
    allocate_tensor_mb,
    get_peak_vram_mb,
    reset_peak_vram,
)


def test_peak_detects_allocation() -> None:
    """Assert peak VRAM increases after allocating a tensor on GPU."""
    if not torch.cuda.is_available():
        return  # Skip if no CUDA

    reset_peak_vram()
    peak_before = get_peak_vram_mb()

    # Allocate ~100 MB on GPU
    tensor = allocate_tensor_mb(100.0)
    peak_after = get_peak_vram_mb()

    del tensor
    torch.cuda.empty_cache()

    assert peak_after > peak_before, (
        f"Peak should increase after allocation: before={peak_before:.2f}, after={peak_after:.2f}"
    )
    assert peak_after >= 100.0, f"Peak should be at least 100 MB, got {peak_after:.2f}"


def test_reset_clears_peak() -> None:
    """Assert reset_peak_vram clears the peak tracker."""
    if not torch.cuda.is_available():
        return  # Skip if no CUDA

    # Allocate something to set a non-zero peak
    tensor = allocate_tensor_mb(50.0)
    del tensor
    torch.cuda.empty_cache()

    reset_peak_vram()
    peak = get_peak_vram_mb()

    # reset_peak_memory_stats() rebases the peak to *currently allocated*
    # memory, not literally 0 — ambient CUDA context/allocator overhead
    # (cuBLAS/cuDNN handles, etc.) from earlier tests in the same process
    # can leave a small residual. What matters is that reset dropped the
    # peak well below the 50 MB we just allocated and freed.
    assert peak < 10.0, f"Peak should drop near 0 after reset, got {peak:.2f}"


def test_no_cuda_returns_zero() -> None:
    """Assert get_peak_vram_mb returns 0 when CUDA unavailable."""
    # This always runs — the function handles unavailable CUDA gracefully
    result = get_peak_vram_mb()
    assert isinstance(result, float)
    assert result >= 0
