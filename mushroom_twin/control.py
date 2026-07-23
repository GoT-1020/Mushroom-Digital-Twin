"""Decision/control layer: actuator controller and alert manager."""

from datetime import datetime

from .config import Config
from .fsm import (
    CO2State,
    ContaminationState,
    HumidityState,
    MasterFSM,
    MoistureState,
    TemperatureState,
)
from .state import TwinState


class ActuatorController:
    """Intelligent actuator controller driven by the MasterFSM states."""

    def __init__(self):
        pass

    def reset(self, state: TwinState) -> None:
        """Turn all actuators off before recomputing this step's commands."""
        state.cooling_pad = False
        state.heater = False
        state.fogger = False
        state.sprinkler = False
        state.exhaust_fan = False
        state.fresh_air_fan = False

    def temperature_control(self, state: TwinState, fsm: MasterFSM) -> None:
        if fsm.temperature_state == TemperatureState.LOW:
            state.heater = True
        elif fsm.temperature_state == TemperatureState.HIGH:
            state.cooling_pad = True
            state.exhaust_fan = True
        elif fsm.temperature_state == TemperatureState.CRITICAL:
            state.cooling_pad = True
            state.exhaust_fan = True
        else:
            state.heater = False
            state.cooling_pad = False

    def humidity_control(
        self, state: TwinState, fsm: MasterFSM, previous_fogger: bool = False
    ) -> None:
        if fsm.humidity_state == HumidityState.LOW:
            state.fogger = True
        elif fsm.humidity_state == HumidityState.HIGH:
            state.fogger = False
            state.exhaust_fan = True
        elif fsm.humidity_state == HumidityState.CRITICAL:
            state.fogger = False
            state.exhaust_fan = True
            state.cooling_pad = False
        elif (
            previous_fogger
            and state.humidity < Config.MIN_HUMIDITY + Config.HUMIDITY_HYSTERESIS
        ):
            # Still recovering: hold the fogger on past the raw threshold so
            # it doesn't chatter on/off every step.
            state.fogger = True
        else:
            state.fogger = False

    def co2_control(self, state: TwinState, fsm: MasterFSM) -> None:
        if fsm.co2_state == CO2State.HIGH:
            state.fresh_air_fan = True
            state.exhaust_fan = True
        elif fsm.co2_state == CO2State.CRITICAL:
            state.fresh_air_fan = True
            state.exhaust_fan = True
        elif fsm.co2_state == CO2State.LOW:
            state.fresh_air_fan = False
        else:
            state.fresh_air_fan = False

    def moisture_control(
        self, state: TwinState, fsm: MasterFSM, previous_sprinkler: bool = False
    ) -> None:
        if fsm.moisture_state == MoistureState.LOW:
            state.sprinkler = True
        elif fsm.moisture_state == MoistureState.HIGH:
            state.sprinkler = False
            state.exhaust_fan = True
        elif (
            previous_sprinkler
            and state.moisture < Config.MIN_MOISTURE + Config.MOISTURE_HYSTERESIS
        ):
            # Still recovering: hold the sprinkler on past the raw threshold
            # so it doesn't chatter on/off every step.
            state.sprinkler = True
        else:
            state.sprinkler = False

    def contamination_control(self, state: TwinState, fsm: MasterFSM) -> None:
        """Control actions for contamination events."""
        if fsm.contamination_state == ContaminationState.WARNING:
            state.exhaust_fan = True
        elif fsm.contamination_state == ContaminationState.CONTAMINATED:
            state.sprinkler = False
            state.fogger = False
            state.exhaust_fan = True
        elif fsm.contamination_state == ContaminationState.EMERGENCY:
            state.sprinkler = False
            state.fogger = False
            state.cooling_pad = False
            state.exhaust_fan = True
            state.fresh_air_fan = False

    def update(self, state: TwinState, fsm: MasterFSM) -> None:
        """Execute complete actuator control for one step."""
        previous_fogger = state.fogger
        previous_sprinkler = state.sprinkler
        self.reset(state)
        self.temperature_control(state, fsm)
        self.humidity_control(state, fsm, previous_fogger)
        self.co2_control(state, fsm)
        self.moisture_control(state, fsm, previous_sprinkler)
        self.contamination_control(state, fsm)

    def get_status(self, state: TwinState) -> dict:
        """Return actuator states."""
        return {
            "Cooling Pad": state.cooling_pad,
            "Heater": state.heater,
            "Fogger": state.fogger,
            "Sprinkler": state.sprinkler,
            "Exhaust Fan": state.exhaust_fan,
            "Fresh Air Fan": state.fresh_air_fan,
        }

    def print_status(self, state: TwinState) -> None:
        print("\n" + "=" * 70)
        print("ACTUATOR STATUS")
        print("=" * 70)
        print(f"Cooling Pad    : {state.cooling_pad}")
        print(f"Heater         : {state.heater}")
        print(f"Fogger         : {state.fogger}")
        print(f"Sprinkler      : {state.sprinkler}")
        print(f"Exhaust Fan    : {state.exhaust_fan}")
        print(f"Fresh Air Fan  : {state.fresh_air_fan}")
        print("=" * 70)

    def validate(self, state: TwinState) -> bool:
        """Validate actuator variables are all booleans."""
        actuator_states = [
            state.cooling_pad,
            state.heater,
            state.fogger,
            state.sprinkler,
            state.exhaust_fan,
            state.fresh_air_fan,
        ]
        return all(isinstance(actuator, bool) for actuator in actuator_states)


class AlertManager:
    """Digital twin alert manager: warning/critical/emergency alert generation."""

    def __init__(self):
        self.alert_history = []

    def add_alert(self, level: str, message: str) -> None:
        """Store a new alert."""
        self.alert_history.append(
            {"Time": datetime.now(), "Level": level, "Message": message}
        )

    def temperature_alert(self, fsm: MasterFSM) -> None:
        if fsm.temperature_state == TemperatureState.HIGH:
            self.add_alert("WARNING", "High chamber temperature.")
        elif fsm.temperature_state == TemperatureState.CRITICAL:
            self.add_alert("EMERGENCY", "Critical chamber temperature.")

    def humidity_alert(self, fsm: MasterFSM) -> None:
        if fsm.humidity_state == HumidityState.LOW:
            self.add_alert("WARNING", "Humidity below optimum.")
        elif fsm.humidity_state == HumidityState.HIGH:
            self.add_alert("WARNING", "Humidity above optimum.")
        elif fsm.humidity_state == HumidityState.CRITICAL:
            self.add_alert("EMERGENCY", "Critical humidity level.")

    def co2_alert(self, fsm: MasterFSM) -> None:
        if fsm.co2_state == CO2State.HIGH:
            self.add_alert("WARNING", "CO₂ concentration is high.")
        elif fsm.co2_state == CO2State.CRITICAL:
            self.add_alert("EMERGENCY", "Critical CO₂ concentration.")

    def moisture_alert(self, fsm: MasterFSM) -> None:
        if fsm.moisture_state == MoistureState.LOW:
            self.add_alert("WARNING", "Substrate moisture is low.")
        elif fsm.moisture_state == MoistureState.HIGH:
            self.add_alert("WARNING", "Substrate moisture is high.")

    def contamination_alert(self, fsm: MasterFSM) -> None:
        # NOTE: unimplemented (`pass`) in the original framework; completed here
        # to match the pattern of the other *_alert methods.
        if fsm.contamination_state == ContaminationState.WARNING:
            self.add_alert("WARNING", "Possible contamination detected.")
        elif fsm.contamination_state == ContaminationState.CONTAMINATED:
            self.add_alert("CRITICAL", "Contamination confirmed.")
        elif fsm.contamination_state == ContaminationState.EMERGENCY:
            self.add_alert("EMERGENCY", "Severe contamination - quarantine required.")

    def update(self, fsm: MasterFSM) -> None:
        # NOTE: unimplemented (`pass`) in the original framework; completed here
        # so that alerts are actually generated each step.
        self.temperature_alert(fsm)
        self.humidity_alert(fsm)
        self.co2_alert(fsm)
        self.moisture_alert(fsm)
        self.contamination_alert(fsm)

    def print_alerts(self) -> None:
        # NOTE: unimplemented (`pass`) in the original framework; completed here.
        print("\n" + "=" * 70)
        print("ALERT HISTORY")
        print("=" * 70)
        if not self.alert_history:
            print("No alerts recorded.")
        else:
            for alert in self.alert_history:
                timestamp = alert["Time"].strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] {alert['Level']:<9}: {alert['Message']}")
        print(f"\nTotal Alerts : {len(self.alert_history)}")
        print("=" * 70)

    def validate(self) -> bool:
        # NOTE: called by IntelligentDigitalTwin.validate_system() but never
        # defined in the original framework; added here to prevent AttributeError.
        return isinstance(self.alert_history, list)
