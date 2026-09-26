"""Central configuration for the NeuroTraffic simulation."""


class Config:
    # Window
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 800
    FPS = 60
    TITLE = "NeuroTraffic"

    # Grid
    GRID_COLS = 4
    GRID_ROWS = 4
    BLOCK_SIZE = 160  # pixels between intersections

    # Road rendering
    ROAD_WIDTH = 30
    LANE_WIDTH = 15

    # Traffic lights
    DEFAULT_PHASE_TIME = 15.0  # seconds per phase (fixed timer)
    MIN_PHASE_TIME = 5.0
    MAX_PHASE_TIME = 30.0

    # Vehicles
    CAR_LENGTH = 12
    CAR_WIDTH = 8
    CAR_MAX_SPEED = 120.0  # pixels per second
    CAR_ACCELERATION = 80.0
    CAR_DECELERATION = 160.0
    SPAWN_CLEARANCE = 24.0  # road entry must be clear this far to spawn
    SPAWN_INTERVAL = 0.6  # seconds between car spawns
    MAX_ACTIVE_CARS = 100

    # Simulation
    SIM_TIMESTEP = 1.0 / 60.0  # fixed physics step; faster speeds run more steps
    MAX_FRAME_TIME = 0.1  # clamp long frames (e.g. window dragged) to avoid a jump

    # Training
    TRAINING_SIM_DURATION = 120.0  # shorter sim for faster training
    TRAINING_STEPS_PER_FRAME = 50  # sim ticks per rendered frame during training

    # Neural network
    BRAIN_INPUTS = 10
    BRAIN_HIDDEN_1 = 16
    BRAIN_HIDDEN_2 = 16
    BRAIN_OUTPUTS = 2

    # Genetic algorithm
    POPULATION_SIZE = 30
    ELITE_COUNT = 5
    MUTATION_RATE = 0.05
    MUTATION_STRENGTH = 0.2

    # Fitness weights
    FIT_CARS_COMPLETED = 20.0
    FIT_AVG_TRAVEL_TIME = -2.0
    FIT_AVG_WAIT_TIME = -3.0
    FIT_CONGESTION = -5.0
    FIT_STUCK_CARS = -3.0
    FIT_ACTIVE_WAIT = -1.5
    FIT_LIGHT_SWITCHES = -0.5

    # Colors
    COLOR_BG = (40, 40, 45)
    COLOR_ROAD = (70, 70, 75)
    COLOR_LANE_MARK = (120, 120, 60)
    COLOR_INTERSECTION = (60, 60, 65)
    COLOR_CAR = (60, 160, 255)
    COLOR_GREEN = (50, 205, 50)
    COLOR_RED = (220, 50, 50)
    COLOR_YELLOW = (255, 200, 50)
    COLOR_TEXT = (220, 220, 220)
    COLOR_DASHBOARD_BG = (30, 30, 35)
