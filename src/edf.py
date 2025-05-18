# edf.py

import heapq
import config

class EDFScheduler:
    def __init__(self):
        self.ready_queue = []
        self.current_ticks = 0
        self.pending_tasks = []
        self.currently_running_task = None
        self.missed_deadlines = 0

    def add_task(self, task):
        heapq.heappush(self.ready_queue, (task.deadline_ticks, task))

    def add_periodic_task(self, task):
        self.pending_tasks.append(task)

    def handle_arrivals(self):
        arrived = [t for t in self.pending_tasks if t.next_arrival_ticks <= self.current_ticks]
        for task in arrived:
            print(f"Task {task.name} arrived at {self.current_ticks/config.TICKS_PER_SECOND:.1f}s with deadline {task.deadline_ticks/config.TICKS_PER_SECOND:.1f}s.")
            self.add_task(task)
            self.pending_tasks.remove(task)
            # Preempt if needed
            if self.currently_running_task and task.deadline_ticks < self.currently_running_task.deadline_ticks:
                print(f"Preempting {self.currently_running_task.name} for {task.name}.")
                self.add_task(self.currently_running_task)
                self.currently_running_task = None

    def check_deadline_misses(self):
        missed = []
        for deadline, task in self.ready_queue:
            if deadline < self.current_ticks:
                print(f"Task {task.name} missed its deadline!")
                self.missed_deadlines += 1
                missed.append((deadline, task))
        for m in missed:
            self.ready_queue.remove(m)
        heapq.heapify(self.ready_queue)

    def schedule(self):
        if not self.ready_queue:
            return None
        _, task = heapq.heappop(self.ready_queue)
        return task

    def advance_time(self, ticks):
        self.current_ticks += ticks


class CC_EDFScheduler(EDFScheduler):
    def __init__(self, safe_frequency):
        super().__init__()
        self.slack_observed = False
        self.safe_frequency = safe_frequency  # never go below this frequency after slack

    def adjust_frequency(self):
        tasks_considered = [t for (_, t) in self.ready_queue]
        if self.currently_running_task:
            tasks_considered.append(self.currently_running_task)

        if not tasks_considered:
            return min(config.AVAILABLE_FREQUENCIES.keys()), config.IDLE_POWER

        D_min = min(t.deadline_ticks for t in tasks_considered)
        time_until_deadline = D_min - self.current_ticks
        if time_until_deadline <= 0:
            return config.MAX_FREQUENCY, config.AVAILABLE_FREQUENCIES[config.MAX_FREQUENCY]

        tasks_for_Dmin = [t for t in tasks_considered if t.deadline_ticks == D_min]
        total_work = sum(t.remaining_ticks for t in tasks_for_Dmin)

        if not self.slack_observed:
            # No slack yet: run at max frequency
            return config.MAX_FREQUENCY, config.AVAILABLE_FREQUENCIES[config.MAX_FREQUENCY]

        # With slack observed, try to reduce frequency, but not below safe_frequency
        frequency_fraction = total_work / time_until_deadline
        # Must not go below safe_frequency
        frequency_fraction = max(frequency_fraction, self.safe_frequency)

        for f in sorted(config.AVAILABLE_FREQUENCIES.keys()):
            if f >= frequency_fraction:
                return f, config.AVAILABLE_FREQUENCIES[f]

        return config.MAX_FREQUENCY, config.AVAILABLE_FREQUENCIES[config.MAX_FREQUENCY]
