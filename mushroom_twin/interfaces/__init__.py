"""Interfaces to external systems: computer vision, ESP32 hardware, dashboard."""

from .vision import ComputerVisionInterface
from .esp32 import ESP32Interface
from .dashboard import DashboardInterface

__all__ = ["ComputerVisionInterface", "ESP32Interface", "DashboardInterface"]
