"""Tests for shared/config_loader.py — using tests/config/hardware.json.

Validates that the test hardware.json loads correctly
and contains the expected concrete values.
"""

from __future__ import annotations

from pathlib import Path

from airllm_benchmark.shared.config_loader import (
    load_hardware,
    validate_hardware,
)

TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class TestRealHardwareConfig:
    """Tests against the test config/hardware.json file."""

    def test_real_hardware_loads(self) -> None:
        """Test hardware.json exists and loads without error."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw is not None

    def test_real_hardware_cpu(self) -> None:
        """CPU is Intel Core i9-13900K."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw.cpu == "Intel Core i9-13900K"

    def test_real_hardware_gpu(self) -> None:
        """GPU is NVIDIA GeForce RTX 4090 24GB."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw.gpu == "NVIDIA GeForce RTX 4090 24GB"

    def test_real_hardware_ram(self) -> None:
        """RAM is 64 GB."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw.ram_gb == 64

    def test_real_hardware_vram(self) -> None:
        """VRAM is 24 GB."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw.vram_gb == 24

    def test_real_hardware_disk(self) -> None:
        """Free disk is 1000 GB."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw.disk_free_gb == 1000

    def test_real_hardware_os(self) -> None:
        """OS is Ubuntu 22.04 LTS."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw.os == "Ubuntu 22.04 LTS"

    def test_real_hardware_documented_by(self) -> None:
        """documented_by is placeholder_user."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw.documented_by == "placeholder_user"

    def test_real_hardware_documented_at(self) -> None:
        """documented_at is 2026-07-03T00:00:00."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw.documented_at == "2026-07-03T00:00:00"

    def test_real_hardware_is_complete(self) -> None:
        """is_complete returns True for test hardware config."""
        hw = load_hardware(TEST_CONFIG_DIR)
        assert hw.is_complete() is True

    def test_real_hardware_passes_validation(self) -> None:
        """validate_hardware does not raise for test hardware config."""
        hw = load_hardware(TEST_CONFIG_DIR)
        validate_hardware(hw)  # should not raise
