# config.py

TIME_QUANTUM = 0.1
TICKS_PER_SECOND = int(round(1 / TIME_QUANTUM))  # e.g., 0.1 -> 10 ticks/sec
SIMULATION_DURATION_SECONDS = 100
SIMULATION_DURATION_TICKS = SIMULATION_DURATION_SECONDS * TICKS_PER_SECOND

TASKS = [
    {"name": "Task1", "execution_time_sec": 10, "period_sec": 20},
    {"name": "Task2", "execution_time_sec": 5, "period_sec": 15},
]

AVAILABLE_FREQUENCIES = {
    1.0: 30,
    1.5: 45,
    1.75: 60,
    2.0: 90,
}

IDLE_POWER = 15

CC_EDF_EXECUTION_TIME_RANGE = {
    "min_percent": 50,
    "max_percent": 80,
}

MAX_FREQUENCY = max(AVAILABLE_FREQUENCIES.keys())
MAX_POWER = AVAILABLE_FREQUENCIES[MAX_FREQUENCY]
