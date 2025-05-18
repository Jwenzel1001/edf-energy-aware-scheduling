# main.py

from edf import EDFScheduler, CC_EDFScheduler
from task import Task
import config
import copy
import math

def calculate_utilization(tasks_info):
    return sum((t["execution_time_sec"] / t["period_sec"]) for t in tasks_info)

def lcm(a, b):
    return a * b // math.gcd(a, b)

def hyperperiod(tasks):
    p = [int(round(t["period_sec"] * config.TICKS_PER_SECOND)) for t in tasks]
    h = p[0]
    for x in p[1:]:
        h = lcm(h, x)
    return h

def get_static_frequency(tasks_info):
    utilization = calculate_utilization(tasks_info)
    max_freq = config.MAX_FREQUENCY
    if utilization > 1:
        # Must use max frequency because the workload exceeds a single CPU at lower speeds
        print("Static: Utilization > 1, using max freq")
        return max_freq, config.AVAILABLE_FREQUENCIES[max_freq]

    # Find the lowest frequency that can handle the given utilization
    required_freq = utilization * max_freq

    for f in sorted(config.AVAILABLE_FREQUENCIES.keys()):
        if f >= required_freq:
            # Do not scale execution_time_sec here.
            # Just return the chosen frequency and power.
            return f, config.AVAILABLE_FREQUENCIES[f]

    # If none found (unlikely), default to max frequency
    return max_freq, config.AVAILABLE_FREQUENCIES[max_freq]


def init_tasks(tasks_info, frequency, power, exec_range=(100,100)):
    task_list = []
    for info in tasks_info:
        t = Task(info["name"], info["execution_time_sec"], info["period_sec"], frequency, power)
        t.set_actual_execution_time(exec_range[0], exec_range[1])
        task_list.append(t)
    return task_list

def simulate_schedule(tasks_info, frequency, power, description):
    print(f"\n{description}")
    print(f"Frequency: {frequency} GHz, Power: {power} W")

    scheduler = EDFScheduler()
    tasks = init_tasks(tasks_info, frequency, power, (100,100))
    for task in tasks:
        scheduler.add_periodic_task(task)

    idle_ticks = 0
    total_energy = 0

    while scheduler.current_ticks < config.SIMULATION_DURATION_TICKS:
        scheduler.handle_arrivals()
        scheduler.check_deadline_misses()

        print(f"\nTime: {scheduler.current_ticks/config.TICKS_PER_SECOND:.1f} s")

        if scheduler.currently_running_task:
            next_task = scheduler.currently_running_task
        else:
            next_task = scheduler.schedule()

        if next_task:
            scheduler.currently_running_task = next_task
            print(f"Executing {next_task.name} deadline={next_task.deadline_ticks/config.TICKS_PER_SECOND:.1f}s")
            completed = next_task.execute(1, frequency)
            energy = power * config.TIME_QUANTUM
            total_energy += energy
            print(f"{next_task.name} consumed {energy:.2f} J")
            if completed:
                print(f"{next_task.name} completed!")
                next_task.reset(100,100)
                scheduler.add_periodic_task(next_task)
                scheduler.currently_running_task = None
        else:
            print("System idle.")
            idle_ticks += 1
            idle_energy = config.IDLE_POWER * config.TIME_QUANTUM
            total_energy += idle_energy
            print(f"Idle consumed {idle_energy:.2f} J")

        scheduler.advance_time(1)

    print(f"\n{description} completed.")
    print(f"Energy: {total_energy:.2f} J, Idle: {idle_ticks*config.TIME_QUANTUM:.2f}s, Missed: {scheduler.missed_deadlines}")
    return total_energy, idle_ticks*config.TIME_QUANTUM, scheduler.missed_deadlines

def simulate_cc_edf(tasks_info, description, safe_frequency):
    print(f"\n{description}")

    scheduler = CC_EDFScheduler(safe_frequency)
    rng = config.CC_EDF_EXECUTION_TIME_RANGE
    tasks = init_tasks(tasks_info, config.MAX_FREQUENCY, config.MAX_POWER, (rng["min_percent"], rng["max_percent"]))
    for t in tasks:
        scheduler.add_periodic_task(t)

    idle_ticks = 0
    total_energy = 0

    while scheduler.current_ticks < config.SIMULATION_DURATION_TICKS:
        scheduler.handle_arrivals()
        scheduler.check_deadline_misses()

        print(f"\nTime: {scheduler.current_ticks/config.TICKS_PER_SECOND:.1f} s")

        current_frequency, current_power = scheduler.adjust_frequency()
        print(f"Freq: {current_frequency} GHz, Power: {current_power} W")

        if scheduler.currently_running_task:
            next_task = scheduler.currently_running_task
        else:
            next_task = scheduler.schedule()

        if next_task:
            scheduler.currently_running_task = next_task
            print(f"Executing {next_task.name} deadline={next_task.deadline_ticks/config.TICKS_PER_SECOND:.1f}s")
            completed = next_task.execute(1, current_frequency)
            energy = current_power * config.TIME_QUANTUM
            total_energy += energy
            print(f"{next_task.name} consumed {energy:.2f} J")
            if completed:
                if next_task.actual_execution_ticks < next_task.worst_case_execution_ticks:
                    scheduler.slack_observed = True
                print(f"{next_task.name} completed!")
                rng = config.CC_EDF_EXECUTION_TIME_RANGE
                next_task.reset(rng["min_percent"], rng["max_percent"])
                scheduler.add_periodic_task(next_task)
                scheduler.currently_running_task = None
        else:
            print("System idle.")
            idle_ticks += 1
            idle_energy = config.IDLE_POWER * config.TIME_QUANTUM
            total_energy += idle_energy
            print(f"Idle consumed {idle_energy:.2f} J")

        scheduler.advance_time(1)

    print(f"\n{description} completed.")
    print(f"Energy: {total_energy:.2f} J, Idle: {idle_ticks*config.TIME_QUANTUM:.2f}s, Missed: {scheduler.missed_deadlines}")
    return total_energy, idle_ticks*config.TIME_QUANTUM, scheduler.missed_deadlines

def main():
    tasks_for_edf = copy.deepcopy(config.TASKS)
    tasks_for_static = copy.deepcopy(config.TASKS)
    tasks_for_cc = copy.deepcopy(config.TASKS)

    utilization = calculate_utilization(tasks_for_edf)
    print(f"Utilization: {utilization:.2f}")

    # Basic EDF at max frequency:
    edf_energy, edf_idle, edf_missed = simulate_schedule(
        tasks_for_edf, config.MAX_FREQUENCY, config.MAX_POWER, "Basic EDF"
    )

    # Static EDF
    static_freq, static_power = get_static_frequency(tasks_for_static)
    static_energy, static_idle, static_missed = simulate_schedule(
        tasks_for_static, static_freq, static_power, "Static EDF"
    )

    # CC-EDF, starting safe and only lowering after slack
    # Use the static_freq found as a safe lower bound
    safe_frequency = static_freq if utilization <= 1 else config.MAX_FREQUENCY
    cc_energy, cc_idle, cc_missed = simulate_cc_edf(tasks_for_cc, "Cycle-Conserving EDF", safe_frequency)

    print("\nComparison of Schedules:")
    print(f"Basic EDF:   E={edf_energy:.2f}J, Idle={edf_idle:.2f}s, Missed={edf_missed}")
    print(f"Static EDF:  E={static_energy:.2f}J, Idle={static_idle:.2f}s, Missed={static_missed}")
    print(f"CC-EDF:      E={cc_energy:.2f}J, Idle={cc_idle:.2f}s, Missed={cc_missed}")

if __name__ == "__main__":
    main()
