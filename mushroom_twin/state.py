"""Digital twin state vector."""

from datetime import datetime

from .config import Config


class TwinState:
    """Represents the complete digital twin state."""

    def __init__(self):
        # Time
        self.current_hour = 0
        self.current_day = 0
        self.timestamp = datetime.now()

        # Growth stage / management
        self.batch_id = "BATCH_001"
        self.current_stage = "Preparation"

        # Environment
        self.temperature = Config.INITIAL_TEMPERATURE
        self.humidity = Config.INITIAL_HUMIDITY
        self.co2 = Config.INITIAL_CO2
        self.moisture = Config.INITIAL_MOISTURE

        # Biological variables
        self.colonization = Config.INITIAL_COLONIZATION
        self.fruit_weight = Config.INITIAL_FRUIT_WEIGHT
        self.pinhead_count = 0
        self.fruit_count = 0
        self.yield_estimate = 0.0

        # Computer vision variables
        self.contamination_level = 0.0
        self.colonization_percentage = Config.INITIAL_COLONIZATION

        # Respiration variables
        self.substrate_respiration = 0.0
        self.fruit_respiration = 0.0
        self.total_respiration = 0.0
        self.respiration_heat = 0.0

        # Health assessment
        self.growth_performance_score = 100.0
        self.environment_score = 100.0
        self.contamination_score = 100.0
        self.health_index = Config.INITIAL_HEALTH_INDEX

        # Actuator states
        self.cooling_pad = Config.COOLING_PAD
        self.heater = Config.HEATER
        self.fogger = Config.FOGGER
        self.sprinkler = Config.SPRINKLER
        self.exhaust_fan = Config.EXHAUST_FAN
        self.fresh_air_fan = Config.FRESH_AIR_FAN

    def update_time(self):
        """Advance simulation by one hour."""
        self.current_hour += 1
        self.current_day = self.current_hour // 24
        self.timestamp = datetime.now()
