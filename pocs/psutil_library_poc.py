"""Library PoC — psutil memory sampling.

Goal: Prove psutil is importable and can measure the current process's RAM usage.
"""

from __future__ import annotations

import psutil


def get_process_ram_mb() -> float:
    """Return current process RSS memory in megabytes."""
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / (1024 * 1024)


if __name__ == "__main__":
    ram_mb = get_process_ram_mb()
    print(f"Current process RAM: {ram_mb:.2f} MB")
    assert ram_mb > 0, "RAM measurement should be positive"
    print("Library PoC PASSED")
