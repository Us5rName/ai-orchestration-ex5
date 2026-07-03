"""Feature PoCs — torch.cuda peak VRAM tracking.

Proves each VRAM-related feature needed by MetricsCollector:
1. Reset peak tracking before a run
2. Capture peak VRAM after allocation
"""

from __future__ import annotations

import torch


def reset_peak_vram() -> None:
    """Reset the CUDA peak memory tracker.

    Must be called before each benchmark run so peak reflects only that run.
    No-op when CUDA is unavailable.
    """
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()


def get_peak_vram_mb() -> float:
    """Return peak CUDA memory allocation in megabytes.

    Returns 0.0 if CUDA is unavailable.
    """
    if not torch.cuda.is_available():
        return 0.0
    return torch.cuda.max_memory_allocated() / (1024 * 1024)


def allocate_tensor_mb(size_mb: float) -> torch.Tensor:
    """Allocate a tensor of the given size on GPU.

    Args:
        size_mb: Approximate megabytes to allocate (float32 = 4 bytes/element).

    Returns:
        Allocated tensor on CUDA.
    """
    num_elements = int(size_mb * 1024 * 1024 / 4)
    return torch.empty(num_elements, dtype=torch.float32, device="cuda")


__all__ = ["reset_peak_vram", "get_peak_vram_mb", "allocate_tensor_mb"]
