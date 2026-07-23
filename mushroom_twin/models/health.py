"""Digital twin health assessment model.

Composite health index = weighted growth + environment + contamination scores.
"""

from ..config import Config
from ..state import TwinState


class HealthModel:
    """Digital twin health assessment model."""

    def __init__(self):
        self.environment_weight = Config.ECS_WEIGHT
        self.growth_weight = Config.GPS_WEIGHT
        self.contamination_weight = Config.CCS_WEIGHT

    @staticmethod
    def _score(
        value: float,
        optimum_min: float,
        optimum_max: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Return a normalized score between 0 and 100."""
        if optimum_min <= value <= optimum_max:
            return 100.0
        if value < optimum_min:
            if value <= minimum:
                return 0.0
            return ((value - minimum) / (optimum_min - minimum)) * 100.0
        if value >= maximum:
            return 0.0
        return ((maximum - value) / (maximum - optimum_max)) * 100.0

    def environment_score(self, state: TwinState) -> float:
        """Environmental health as the mean of T/H/CO2/M sub-scores."""
        temperature_score = self._score(
            state.temperature, Config.MIN_TEMPERATURE, Config.MAX_TEMPERATURE, 15.0, 40.0
        )
        humidity_score = self._score(
            state.humidity, Config.MIN_HUMIDITY, Config.MAX_HUMIDITY, 50.0, 100.0
        )
        co2_score = self._score(
            state.co2, Config.MIN_CO2, Config.MAX_CO2, 400.0, Config.MAX_ALLOWED_CO2
        )
        moisture_score = self._score(
            state.moisture, Config.MIN_MOISTURE, Config.MAX_MOISTURE, 30.0, 100.0
        )

        environment = (
            temperature_score + humidity_score + co2_score + moisture_score
        ) / 4.0
        state.environment_score = environment
        return environment

    def growth_score(self, state: TwinState) -> float:
        """Growth health based on colonization percentage."""
        score = max(0.0, min(state.colonization, 100.0))
        state.growth_performance_score = score
        return score

    def contamination_score(self, state: TwinState) -> float:
        """Contamination score = 100 - contamination level."""
        contamination = max(0.0, min(state.contamination_level, 100.0))
        score = 100.0 - contamination
        state.contamination_score = score
        return score

    def health_index(self, state: TwinState) -> float:
        """Overall weighted health index (0-100)."""
        health = (
            self.growth_weight * state.growth_performance_score
            + self.environment_weight * state.environment_score
            + self.contamination_weight * state.contamination_score
        )
        state.health_index = max(0.0, min(health, 100.0))
        return state.health_index

    def health_status(self, state: TwinState) -> str:
        """Return the health category label."""
        health = state.health_index
        if health >= 90.0:
            return "EXCELLENT"
        elif health >= 80.0:
            return "HEALTHY"
        elif health >= 60.0:
            return "WARNING"
        return "CRITICAL"

    def update(self, state: TwinState) -> None:
        """Execute one complete health assessment."""
        self.environment_score(state)
        self.growth_score(state)
        self.contamination_score(state)
        self.health_index(state)

    def get_health_status(self, state: TwinState) -> dict:
        """Return all health information."""
        return {
            "Environment Score": state.environment_score,
            "Growth Score": state.growth_performance_score,
            "Contamination Score": state.contamination_score,
            "Health Index": state.health_index,
            "Health Status": self.health_status(state),
        }

    def print_status(self, state: TwinState) -> None:
        print("\n" + "=" * 60)
        print("HEALTH MODEL")
        print("=" * 60)
        print(f"Environment Score   : {state.environment_score:.2f}")
        print(f"Growth Score        : {state.growth_performance_score:.2f}")
        print(f"Contamination Score : {state.contamination_score:.2f}")
        print(f"Health Index        : {state.health_index:.2f}")
        print(f"Overall Status      : {self.health_status(state)}")
        print("=" * 60)

    def validate(self, state: TwinState) -> bool:
        """Validate health variables are within 0-100."""
        if not 0.0 <= state.environment_score <= 100.0:
            return False
        if not 0.0 <= state.growth_performance_score <= 100.0:
            return False
        if not 0.0 <= state.contamination_score <= 100.0:
            return False
        if not 0.0 <= state.health_index <= 100.0:
            return False
        return True
