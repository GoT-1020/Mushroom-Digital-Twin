"""Biological growth model: logistic colonization + Gompertz fruiting."""

import math

from ..config import Config
from ..state import TwinState


class GrowthModel:
    """Biological growth model (colonization, fruiting, yield)."""

    def __init__(self):
        # Logistic growth parameters
        self.mu_max = Config.MU_MAX
        self.max_colonization = Config.MAX_COLONIZATION

        # Gompertz parameters
        self.w_max = Config.W_MAX
        self.k = Config.GOMPERTZ_K
        self.t0 = Config.GOMPERTZ_T0
        self.pinning_threshold = Config.PINNING_THRESHOLD

    @staticmethod
    def _linear_score(
        value: float,
        optimum_min: float,
        optimum_max: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Return a normalized score between 0 and 1 for a variable."""
        if optimum_min <= value <= optimum_max:
            return 1.0
        if value < optimum_min:
            if value <= minimum:
                return 0.0
            return (value - minimum) / (optimum_min - minimum)
        if value >= maximum:
            return 0.0
        return (maximum - value) / (maximum - optimum_max)

    def environmental_modifier(self, state: TwinState) -> float:
        """Effective growth modifier: mu_eff = mu_max * fT * fH * fCO2 * fM."""
        f_temperature = self._linear_score(
            state.temperature, Config.MIN_TEMPERATURE, Config.MAX_TEMPERATURE, 15.0, 40.0
        )
        f_humidity = self._linear_score(
            state.humidity, Config.MIN_HUMIDITY, Config.MAX_HUMIDITY, 50.0, 100.0
        )
        f_co2 = self._linear_score(
            state.co2, Config.MIN_CO2, Config.MAX_CO2, 400.0, 5000.0
        )
        f_moisture = self._linear_score(
            state.moisture, Config.MIN_MOISTURE, Config.MAX_MOISTURE, 30.0, 100.0
        )

        modifier = f_temperature * f_humidity * f_co2 * f_moisture
        return max(0.0, min(modifier, 1.0))

    def update_colonization(self, state: TwinState) -> None:
        """Logistic colonization model: dC/dt = mu_eff * C * (1 - C/K)."""
        modifier = self.environmental_modifier(state)
        mu_effective = self.mu_max * modifier

        growth_rate = (
            mu_effective
            * state.colonization
            * (1.0 - (state.colonization / self.max_colonization))
        )

        state.colonization += Config.TIME_STEP * growth_rate
        if state.colonization > self.max_colonization:
            state.colonization = self.max_colonization

        state.colonization_percentage = state.colonization

    def update_fruit_growth(self, state: TwinState) -> None:
        """Gompertz fruit growth: W(t) = Wmax * exp(-exp(-k(t - t0)))."""
        # Fruiting starts only after sufficient colonization.
        if state.colonization < self.pinning_threshold:
            state.fruit_weight = 0.0
            state.pinhead_count = 0
            state.fruit_count = 0
            return

        simulation_day = state.current_hour / 24.0

        fruit_weight = self.w_max * math.exp(
            -math.exp(-self.k * (simulation_day - self.t0))
        )
        fruit_weight = max(0.0, fruit_weight)

        state.fruit_weight = fruit_weight
        state.pinhead_count = int(max(1, fruit_weight / 12.0))
        state.fruit_count = int(max(1, fruit_weight / 35.0))

    def estimate_yield(self, state: TwinState) -> None:
        """Estimated yield equals current fruit weight (v2.0)."""
        state.yield_estimate = state.fruit_weight

    def get_growth_status(self, state: TwinState) -> dict:
        return {
            "Colonization (%)": state.colonization,
            "Fruit Weight (g)": state.fruit_weight,
            "Pinhead Count": state.pinhead_count,
            "Fruit Count": state.fruit_count,
            "Yield (g)": state.yield_estimate,
        }

    def print_status(self, state: TwinState) -> None:
        print("\n" + "=" * 60)
        print("GROWTH MODEL")
        print("=" * 60)
        print(f"Colonization : {state.colonization:.2f}%")
        print(f"Fruit Weight : {state.fruit_weight:.2f} g")
        print(f"Pinheads     : {state.pinhead_count}")
        print(f"Fruit Count  : {state.fruit_count}")
        print(f"Yield        : {state.yield_estimate:.2f} g")
        print("=" * 60)

    def update(self, state: TwinState) -> None:
        """Execute one biological growth step."""
        self.update_colonization(state)
        self.update_fruit_growth(state)
        self.estimate_yield(state)

    def validate(self, state: TwinState) -> bool:
        """Validate biological variables."""
        if not 0.0 <= state.colonization <= 100.0:
            return False
        if state.fruit_weight < 0.0:
            return False
        if state.yield_estimate < 0.0:
            return False
        return True
