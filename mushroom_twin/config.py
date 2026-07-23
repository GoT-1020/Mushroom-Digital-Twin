"""Global configuration parameters for the mushroom digital twin."""


class Config:
    """Global configuration parameters."""

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    TIME_STEP = 1.0                      # hour
    SIMULATION_DAYS = 30
    HOURS_PER_DAY = 24
    TOTAL_STEPS = SIMULATION_DAYS * HOURS_PER_DAY

    # ------------------------------------------------------------------
    # Chamber Geometry
    # ------------------------------------------------------------------
    CHAMBER_LENGTH = 4.0                 # m
    CHAMBER_WIDTH = 3.0                  # m
    CHAMBER_HEIGHT = 2.5                 # m
    CHAMBER_VOLUME = CHAMBER_LENGTH * CHAMBER_WIDTH * CHAMBER_HEIGHT

    # ------------------------------------------------------------------
    # Initial Environmental Conditions
    # ------------------------------------------------------------------
    INITIAL_TEMPERATURE = 28.0           # °C
    INITIAL_HUMIDITY = 85.0              # %
    INITIAL_CO2 = 1000.0                 # ppm
    INITIAL_MOISTURE = 70.0              # %
    AMBIENT_TEMPERATURE = 30.0           # °C
    AMBIENT_HUMIDITY = 55.0              # % (outside/inlet air pulled in by the exhaust fan)

    # ------------------------------------------------------------------
    # Initial Biological Conditions
    # ------------------------------------------------------------------
    INITIAL_COLONIZATION = 1.0           # %
    INITIAL_FRUIT_WEIGHT = 0.0           # g
    INITIAL_HEALTH_INDEX = 100.0

    # ------------------------------------------------------------------
    # Environmental Thresholds
    # ------------------------------------------------------------------
    MIN_TEMPERATURE = 26.0
    MAX_TEMPERATURE = 30.0
    MIN_HUMIDITY = 80.0
    MAX_HUMIDITY = 90.0
    MIN_CO2 = 800.0
    MAX_CO2 = 1500.0
    MIN_MOISTURE = 60.0
    MAX_MOISTURE = 80.0

    # Hysteresis margins: once triggered by a LOW reading, the fogger/sprinkler
    # stay on until the reading recovers this far past the threshold, instead
    # of switching off the instant it ticks back above MIN_*. Without this,
    # the actuator flips off after a single step, the value drains back below
    # threshold within a couple of hours, and the FSM re-triggers it, alert
    # and all, over and over.
    HUMIDITY_HYSTERESIS = 5.0
    MOISTURE_HYSTERESIS = 5.0
    TEMPERATURE_HYSTERESIS = 2.0

    # ------------------------------------------------------------------
    # Environment Model Coefficients
    # ------------------------------------------------------------------
    KA = 0.08
    KC = 0.60
    KH = 0.45
    KR = 0.01

    KF = 1.20
    # Ventilation exchange coefficient: %/hr of humidity removed per % that
    # the chamber is above AMBIENT_HUMIDITY (proportional, like the KA
    # ambient-temperature exchange term below), not a flat rate. A flat rate
    # can't keep up with transpiration_gain (KT * fruit_weight) once fruit
    # bodies are heavy, so humidity used to pin at the 100% clamp for the
    # entire fruiting stage.
    KV = 0.15
    KT = 0.02

    KS = 0.80
    KG = 0.005

    ALPHA = 0.015
    BETA = 0.010

    BASELINE_CO2 = 420.0
    MAX_ALLOWED_CO2 = 5000.0

    CO2_VENTILATION = 60.0

    # ------------------------------------------------------------------
    # Biological Model
    # ------------------------------------------------------------------
    MU_MAX = 0.020
    MAX_COLONIZATION = 100.0
    PINNING_THRESHOLD = 90.0
    W_MAX = 250.0
    GOMPERTZ_K = 0.25
    GOMPERTZ_T0 = 20.0

    # ------------------------------------------------------------------
    # Respiration Model - Jung & Son (2021)
    # ------------------------------------------------------------------
    A1 = 143.370
    A2 = 0.013
    A3 = -137.343

    # ------------------------------------------------------------------
    # Thornley Respiration
    # ------------------------------------------------------------------
    MAINTENANCE_COEFFICIENT = 0.10
    GROWTH_COEFFICIENT = 0.05
    RESPIRATION_HEAT_COEFFICIENT = 0.01

    # ------------------------------------------------------------------
    # Health Index Weights
    # ------------------------------------------------------------------
    GPS_WEIGHT = 0.40
    ECS_WEIGHT = 0.30
    CCS_WEIGHT = 0.30

    # ------------------------------------------------------------------
    # Actuator Initial States
    # ------------------------------------------------------------------
    COOLING_PAD = False
    HEATER = False
    FOGGER = False
    SPRINKLER = False
    EXHAUST_FAN = False
    FRESH_AIR_FAN = False
