# task.py

import random
import config

class Task:
    def __init__(self, name, execution_time_sec, period_sec, frequency, power, deadline_ticks=None):
        self.name = name
        self.worst_case_execution_ticks = int(round(execution_time_sec * config.TICKS_PER_SECOND))
        self.period_ticks = int(round(period_sec * config.TICKS_PER_SECOND))
        self.frequency = frequency
        self.power = power
        self.deadline_ticks = deadline_ticks if deadline_ticks is not None else self.period_ticks
        self.next_arrival_ticks = 0
        self.actual_execution_ticks = self.worst_case_execution_ticks
        self.remaining_ticks = self.worst_case_execution_ticks

    def set_actual_execution_time(self, min_percent=100, max_percent=100):
        if min_percent < 100 or max_percent < 100:
            min_fraction = min_percent / 100.0
            max_fraction = max_percent / 100.0
            exec_time = random.uniform(min_fraction, max_fraction) * self.worst_case_execution_ticks
        else:
            exec_time = self.worst_case_execution_ticks
        self.actual_execution_ticks = max(1, int(round(exec_time)))
        self.remaining_ticks = self.actual_execution_ticks

    def execute(self, ticks, current_frequency):
        work_per_tick = current_frequency / config.MAX_FREQUENCY
        work_done = ticks * work_per_tick
        self.remaining_ticks -= work_done
        if self.remaining_ticks <= 0:
            self.remaining_ticks = 0
            return True
        return False

    def reset(self, min_percent=100, max_percent=100):
        print(f"Resetting {self.name}: Old deadline = {self.deadline_ticks/config.TICKS_PER_SECOND:.1f}s")
        self.set_actual_execution_time(min_percent, max_percent)
        self.deadline_ticks += self.period_ticks
        self.next_arrival_ticks += self.period_ticks
        print(f"{self.name}: New deadline = {self.deadline_ticks/config.TICKS_PER_SECOND:.1f}s, "
              f"Execution Time = {self.actual_execution_ticks} ticks")

    def scale_execution_time(self, scale_factor):
        # Scale the WCET by scale_factor (max_freq/freq), reducing execution time.
        new_wcet = int(round(self.worst_case_execution_ticks / scale_factor))
        if new_wcet < 1: new_wcet = 1
        self.worst_case_execution_ticks = new_wcet
        # Actual execution time resets to WCET for static
        self.actual_execution_ticks = self.worst_case_execution_ticks
        self.remaining_ticks = self.worst_case_execution_ticks

    def __lt__(self, other):
        return self.deadline_ticks < other.deadline_ticks
