"""Scientific Digital Twin for Oyster Mushroom Cultivation.

A physics + biology simulation of a controlled-environment cultivation chamber
with a control/decision layer (FSMs, actuator controller, alerts) and stubbed
interfaces for hardware (ESP32/MQTT), computer vision, and a dashboard.

Refactored from the original single-file framework by Lakshmi K (v2.0).
"""

from .config import Config
from .state import TwinState
from .orchestrator import DigitalTwin, IntelligentDigitalTwin

__all__ = ["Config", "TwinState", "DigitalTwin", "IntelligentDigitalTwin"]
__version__ = "2.0"
