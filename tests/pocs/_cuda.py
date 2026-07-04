"""Shared CUDA-availability check for real-hardware PoC tests.

Centralizes the check so pytest.mark.skipif guards across the AirLLM
and GPU PoC files don't each duplicate the try/except import.
"""

from __future__ import annotations


def has_cuda() -> bool:
    """Return True if a CUDA device is usable via torch."""
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False
