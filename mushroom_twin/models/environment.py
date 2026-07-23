"""Physical environment model for the cultivation chamber.

Models temperature, humidity, CO2 and substrate moisture dynamics using
first-order / mass-balance formulations integrated with explicit Euler.
"""

from ..config import Config
from ..state import TwinState


class EnvironmentModel:
    """Physical environment model for the mushroom cultivation chamber."""

    def __init__(self):
        # Temperature model parameters
        self.ka = Config.KA
        self.kc = Config.KC
        self.kh = Config.KH
        self.kr = Config.KR

        # Humidity model parameters
        self.kf = Config.KF
        self.kv = Config.KV
        self.kt = Config.KT

        # Moisture model parameters
        self.ks = Config.KS
        self.kg = Config.KG

        # Evaporation parameters
        self.alpha = Config.ALPHA
        self.beta = Config.BETA

        # Ambient conditions
        self.ambient_temperature = Config.AMBIENT_TEMPERATURE

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        """Restrict a value within a specified range."""
        return max(minimum, min(value, maximum))

    def evaporation_rate(self, temperature: float, humidity: float) -> float:
        """Evaporation coefficient: ke = alpha*(T - 20) + beta*(100 - H)."""
        evaporation = (
            self.alpha * (temperature - 20.0)
            + self.beta * (100.0 - humidity)
        )
        return max(evaporation, 0.0)

    def update_temperature(self, state: TwinState) -> None:
        """First-order chamber thermal dynamics."""
        ambient_heat = self.ka * (self.ambient_temperature - state.temperature)

        cooling_effect = self.kc if state.cooling_pad else 0.0
        heating_effect = self.kh if state.heater else 0.0
        respiration_effect = self.kr * state.respiration_heat

        delta_temperature = (
            ambient_heat - cooling_effect + heating_effect + respiration_effect
        )

        state.temperature += Config.TIME_STEP * delta_temperature
        state.temperature = self._clamp(state.temperature, 0.0, 50.0)

    def update_humidity(self, state: TwinState) -> None:
        """Humidity dynamics: fogging + transpiration - ventilation - evaporation."""
        evaporation_loss = self.evaporation_rate(state.temperature, state.humidity)
        fogger_gain = self.kf if state.fogger else 0.0
        ventilation_loss = self.kv if state.exhaust_fan else 0.0
        transpiration_gain = self.kt * state.fruit_weight

        delta_humidity = (
            fogger_gain - ventilation_loss + transpiration_gain - evaporation_loss
        )
        state.humidity += Config.TIME_STEP * delta_humidity

    def update_co2(self, state: TwinState) -> None:
        """Chamber CO2 mass balance: generation - ventilation."""
        generation = state.total_respiration

        if state.exhaust_fan:
            ventilation = Config.CO2_VENTILATION
        elif state.fresh_air_fan:
            ventilation = Config.CO2_VENTILATION * 0.60
        else:
            ventilation = 0.0

        delta_co2 = generation / Config.CHAMBER_VOLUME - ventilation
        state.co2 += Config.TIME_STEP * delta_co2

    def update_moisture(self, state: TwinState) -> None:
        """Substrate moisture: irrigation - evaporation - biological consumption."""
        irrigation = self.ks if state.sprinkler else 0.0
        evaporation = self.evaporation_rate(state.temperature, state.humidity)
        biological_loss = self.kg * state.colonization

        delta_moisture = irrigation - evaporation - biological_loss
        state.moisture += Config.TIME_STEP * delta_moisture

    def apply_limits(self, state: TwinState) -> None:
        """Restrict all environmental variables to physically meaningful ranges."""
        state.temperature = self._clamp(state.temperature, 0.0, 50.0)
        state.humidity = self._clamp(state.humidity, 0.0, 100.0)
        state.co2 = self._clamp(state.co2, Config.BASELINE_CO2, Config.MAX_ALLOWED_CO2)
        state.moisture = self._clamp(state.moisture, 0.0, 100.0)

    def update(self, state: TwinState) -> None:
        """Update the complete chamber environment for one simulation step."""
        self.update_temperature(state)
        self.update_humidity(state)
        self.update_co2(state)
        self.update_moisture(state)
        self.apply_limits(state)

    def get_environment_status(self, state: TwinState) -> dict:
        """Return the current environmental conditions."""
        return {
            "Temperature": state.temperature,
            "Humidity": state.humidity,
            "CO2": state.co2,
            "Moisture": state.moisture,
        }

    def print_status(self, state: TwinState) -> None:
        """Print the current environmental state."""
        print("\n" + "=" * 60)
        print("ENVIRONMENT STATUS")
        print("=" * 60)
        print(f"Temperature : {state.temperature:.2f} °C")
        print(f"Humidity    : {state.humidity:.2f} %")
        print(f"CO₂         : {state.co2:.2f} ppm")
        print(f"Moisture    : {state.moisture:.2f} %")
        print("=" * 60)

    def reset(self, state: TwinState) -> None:
        """Reset environmental variables to their initial values."""
        state.temperature = Config.INITIAL_TEMPERATURE
        state.humidity = Config.INITIAL_HUMIDITY
        state.co2 = Config.INITIAL_CO2
        state.moisture = Config.INITIAL_MOISTURE

    def validate(self, state: TwinState) -> bool:
        """Validate environmental variables are within physical ranges."""
        if not 0.0 <= state.temperature <= 50.0:
            return False
        if not 0.0 <= state.humidity <= 100.0:
            return False
        if not Config.BASELINE_CO2 <= state.co2 <= Config.MAX_ALLOWED_CO2:
            return False
        if not 0.0 <= state.moisture <= 100.0:
            return False
        return True
