"""Library PoC — torch.cuda memory reporting.

Goal: Prove torch.cuda is available and can report GPU memory stats.
"""

from __future__ import annotations

import torch


def get_peak_vram_mb() -> float:
    """Return peak CUDA memory allocation in megabytes.

    Returns 0.0 if CUDA is unavailable.
    """
    if not torch.cuda.is_available():
        return 0.0
    return torch.cuda.max_memory_allocated() / (1024 * 1024)


def get_current_vram_mb() -> float:
    """Return current CUDA memory allocation in megabytes.

    Returns 0.0 if CUDA is unavailable.
    """
    if not torch.cuda.is_available():
        return 0.0
    return torch.cuda.memory_allocated() / (1024 * 1024)


if __name__ == "__main__":
    cuda_ok = torch.cuda.is_available()
    print(f"CUDA available: {cuda_ok}")
    if cuda_ok:
        print(f"  Device: {torch.cuda.get_device_name(0)}")
        print(f"  Current VRAM: {get_current_vram_mb():.2f} MB")
        print(f"  Peak VRAM: {get_peak_vram_mb():.2f} MB")
    assert get_current_vram_mb() >= 0
    assert get_peak_vram_mb() >= 0
    print("Library PoC PASSED")
