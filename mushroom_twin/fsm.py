"""Finite state machine engine: subsystem state enums + MasterFSM supervisor."""

from enum import Enum

from .config import Config
from .state import TwinState


class EnvironmentState(Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class TemperatureState(Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HumidityState(Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CO2State(Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MoistureState(Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class ContaminationState(Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    CONTAMINATED = "CONTAMINATED"
    EMERGENCY = "EMERGENCY"


class EquipmentState(Enum):
    NORMAL = "NORMAL"
    ACTIVE = "ACTIVE"
    FAILURE = "FAILURE"


class MasterFSM:
    """Master finite state machine supervising all subsystem FSMs."""

    def __init__(self):
        self.environment_state = EnvironmentState.NORMAL
        self.temperature_state = TemperatureState.NORMAL
        self.humidity_state = HumidityState.NORMAL
        self.co2_state = CO2State.NORMAL
        self.moisture_state = MoistureState.NORMAL
        self.contamination_state = ContaminationState.SAFE
        self.equipment_state = EquipmentState.NORMAL

    def update_temperature(self, state: TwinState) -> None:
        if state.temperature < Config.MIN_TEMPERATURE:
            self.temperature_state = TemperatureState.LOW
        elif state.temperature > 33.0:
            self.temperature_state = TemperatureState.CRITICAL
        elif state.temperature > Config.MAX_TEMPERATURE:
            self.temperature_state = TemperatureState.HIGH
        else:
            self.temperature_state = TemperatureState.NORMAL

    def update_humidity(self, state: TwinState) -> None:
        if state.humidity < Config.MIN_HUMIDITY:
            self.humidity_state = HumidityState.LOW
        elif state.humidity > 95.0:
            self.humidity_state = HumidityState.CRITICAL
        elif state.humidity > Config.MAX_HUMIDITY:
            self.humidity_state = HumidityState.HIGH
        else:
            self.humidity_state = HumidityState.NORMAL

    def update_co2(self, state: TwinState) -> None:
        if state.co2 < Config.MIN_CO2:
            self.co2_state = CO2State.LOW
        elif state.co2 > 2000:
            self.co2_state = CO2State.CRITICAL
        elif state.co2 > Config.MAX_CO2:
            self.co2_state = CO2State.HIGH
        else:
            self.co2_state = CO2State.NORMAL

    def update_moisture(self, state: TwinState) -> None:
        if state.moisture < Config.MIN_MOISTURE:
            self.moisture_state = MoistureState.LOW
        elif state.moisture > Config.MAX_MOISTURE:
            self.moisture_state = MoistureState.HIGH
        else:
            self.moisture_state = MoistureState.NORMAL

    def update_contamination(self, state: TwinState) -> None:
        contamination = state.contamination_level
        if contamination >= 30:
            self.contamination_state = ContaminationState.EMERGENCY
        elif contamination >= 10:
            self.contamination_state = ContaminationState.CONTAMINATED
        elif contamination > 0:
            self.contamination_state = ContaminationState.WARNING
        else:
            self.contamination_state = ContaminationState.SAFE

    def update_environment(self) -> None:
        """Determine the overall environmental state from all subsystem FSMs."""
        if (
            self.temperature_state == TemperatureState.CRITICAL
            or self.humidity_state == HumidityState.CRITICAL
            or self.co2_state == CO2State.CRITICAL
            or self.contamination_state == ContaminationState.EMERGENCY
        ):
            self.environment_state = EnvironmentState.EMERGENCY
            return

        if (
            self.temperature_state == TemperatureState.HIGH
            or self.humidity_state == HumidityState.HIGH
            or self.co2_state == CO2State.HIGH
            or self.contamination_state == ContaminationState.CONTAMINATED
        ):
            self.environment_state = EnvironmentState.CRITICAL
            return

        if (
            self.temperature_state == TemperatureState.LOW
            or self.humidity_state == HumidityState.LOW
            or self.co2_state == CO2State.LOW
            or self.moisture_state == MoistureState.LOW
            or self.contamination_state == ContaminationState.WARNING
        ):
            self.environment_state = EnvironmentState.WARNING
            return

        self.environment_state = EnvironmentState.NORMAL

    def update_equipment(self, state: TwinState) -> None:
        """Determine whether any actuator is active."""
        active = (
            state.cooling_pad
            or state.heater
            or state.fogger
            or state.sprinkler
            or state.exhaust_fan
            or state.fresh_air_fan
        )
        self.equipment_state = EquipmentState.ACTIVE if active else EquipmentState.NORMAL

    def update(self, state: TwinState) -> None:
        """Execute one complete FSM update."""
        self.update_temperature(state)
        self.update_humidity(state)
        self.update_co2(state)
        self.update_moisture(state)
        self.update_contamination(state)
        self.update_environment()
        self.update_equipment(state)

    def get_status(self) -> dict:
        """Return all FSM states."""
        return {
            "Environment": self.environment_state.value,
            "Temperature": self.temperature_state.value,
            "Humidity": self.humidity_state.value,
            "CO2": self.co2_state.value,
            "Moisture": self.moisture_state.value,
            "Contamination": self.contamination_state.value,
            "Equipment": self.equipment_state.value,
        }

    def print_status(self) -> None:
        print("\n" + "=" * 70)
        print("MASTER FSM STATUS")
        print("=" * 70)
        print(f"Environment   : {self.environment_state.value}")
        print(f"Temperature   : {self.temperature_state.value}")
        print(f"Humidity      : {self.humidity_state.value}")
        print(f"CO₂           : {self.co2_state.value}")
        print(f"Moisture      : {self.moisture_state.value}")
        print(f"Contamination : {self.contamination_state.value}")
        print(f"Equipment     : {self.equipment_state.value}")
        print("=" * 70)
