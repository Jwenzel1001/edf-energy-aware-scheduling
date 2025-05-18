import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from task import Task
from edf import EDFScheduler, CC_EDFScheduler
import config
from main import calculate_utilization
import copy

class SchedulerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EDF Scheduler Visualizer")
        self.geometry("920x1000")
        ctk.set_appearance_mode("light")

        self.tasks = []
        self.scheduler = EDFScheduler()

        # ================= UI FRAMES ================= #
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, padx=10, fill="x")

        self.task_list_frame = ctk.CTkFrame(self)
        self.task_list_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.task_list_frame.columnconfigure(0, weight=1)  
        self.task_list_frame.columnconfigure(1, weight=1)  

        self.schedule_frame = ctk.CTkFrame(self)
        self.schedule_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # ================= INPUT SECTION ================= #
        ctk.CTkLabel(self.input_frame, text="Period (sec)").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(self.input_frame, text="Execution Time (sec)").grid(row=0, column=1, padx=5, pady=5)

        self.period_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Period in seconds")
        self.period_entry.grid(row=1, column=0, padx=5, pady=5)
        self.execution_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Execution Time in seconds")
        self.execution_entry.grid(row=1, column=1, padx=5, pady=5)

        self.add_button = ctk.CTkButton(self.input_frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=1, column=2, padx=5, pady=5)

        # ================= ADD FREQUENCY SECTION ================= #
        ctk.CTkLabel(self.input_frame, text="Frequency").grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.new_freq_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Frequency (GHz)")
        self.new_freq_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        self.new_power_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Power (W)")
        self.new_power_entry.grid(row=1, column=4, padx=5, pady=5, sticky="w")

        self.add_freq_button = ctk.CTkButton(self.input_frame, text="Add Frequency", command=self.add_frequency)
        self.add_freq_button.grid(row=1, column=5, padx=5, pady=5)

        # ================= LEFT AND RIGHT FRAMES ================= #
        self.left_frame = ctk.CTkFrame(self.task_list_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.right_frame = ctk.CTkFrame(self.task_list_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # ================= LEFT SIDE: TASK LIST ================= #
        self.utilization_label = ctk.CTkLabel(self.left_frame, text="Task Set Utilization: 0.00%")
        self.utilization_label.grid(row=0, column=0, pady=5)

        self.task_list_label = ctk.CTkLabel(self.left_frame, text="Tasks", font=("Georgia", 12, "bold"))
        self.task_list_label.grid(row=1, column=0, pady=5)

        self.task_listbox = tk.Listbox(self.left_frame, height=10, width=30, selectmode=tk.SINGLE)
        self.task_listbox.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        self.delete_button = ctk.CTkButton(self.left_frame, text="Delete Task", command=self.delete_task)
        self.delete_button.grid(row=3, column=0, pady=5)

        # Current Settings
        self.viewed_settings_label = ctk.CTkLabel(self.left_frame, text="Current Configuration", font=("Georgia", 12, "bold"))
        self.viewed_settings_label.grid(row=4, column=0, pady=(5, 0))

        self.update_viewed_settings_display()

        # ================= RIGHT SIDE: CONFIGURATION SETTINGS ================= #
        self.config_label = ctk.CTkLabel(self.right_frame, text="Frequency Settings", font=("Georgia", 12, "bold"))
        self.config_label.grid(row=0, column=0, columnspan=2, sticky="n", pady=5)

        ctk.CTkLabel(self.right_frame, text="Available Frequencies (GHz: Watts):").grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
        self.freq_listbox = tk.Listbox(self.right_frame, height=6, width=25)
        self.freq_listbox.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.refresh_frequency_listbox()

        self.remove_freq_button = ctk.CTkButton(self.right_frame, text="Remove Frequency", command=self.remove_frequency)
        self.remove_freq_button.grid(row=6, column=1, padx=5, pady=5, sticky="e")

        # Simulation Configuration Title
        self.sim_config_label = ctk.CTkLabel(self.right_frame, text="Other Settings", font=("Georgia", 12, "bold"))
        self.sim_config_label.grid(row=7, column=0, columnspan=2, sticky="n", pady=(10, 5))

        ctk.CTkLabel(self.right_frame, text="Simulation Duration (sec)").grid(row=8, column=0, sticky="w", padx=5)
        self.sim_duration_entry = ctk.CTkEntry(self.right_frame, placeholder_text=f"{config.SIMULATION_DURATION_SECONDS}")
        self.sim_duration_entry.grid(row=8, column=1, sticky="e", padx=5)

        ctk.CTkLabel(self.right_frame, text="Time Quantum (sec)").grid(row=9, column=0, sticky="w", padx=5)
        self.time_quantum_entry = ctk.CTkEntry(self.right_frame, placeholder_text=f"{config.TIME_QUANTUM}")
        self.time_quantum_entry.grid(row=9, column=1, sticky="e", padx=5)

        ctk.CTkLabel(self.right_frame, text="Idle Power (W)").grid(row=10, column=0, sticky="w", padx=5)
        self.idle_power_entry = ctk.CTkEntry(self.right_frame, placeholder_text=f"{config.IDLE_POWER}")
        self.idle_power_entry.grid(row=10, column=1, sticky="e", padx=5)

        ctk.CTkLabel(self.right_frame, text="CC-EDF Min %").grid(row=11, column=0, sticky="w", padx=5)
        self.cc_min_entry = ctk.CTkEntry(self.right_frame, placeholder_text=f"{config.CC_EDF_EXECUTION_TIME_RANGE['min_percent']}")
        self.cc_min_entry.grid(row=11, column=1, sticky="e", padx=5)

        ctk.CTkLabel(self.right_frame, text="CC-EDF Max %").grid(row=12, column=0, sticky="w", padx=5)
        self.cc_max_entry = ctk.CTkEntry(self.right_frame, placeholder_text=f"{config.CC_EDF_EXECUTION_TIME_RANGE['max_percent']}")
        self.cc_max_entry.grid(row=12, column=1, sticky="e", padx=5)

        self.apply_settings_button = ctk.CTkButton(self.right_frame, text="Apply Settings", command=self.apply_settings)
        self.apply_settings_button.grid(row=13, column=1, sticky="se", padx=5, pady=5)

        # ================= SCHEDULE SECTION ================= #
        self.schedule_button = ctk.CTkButton(self.schedule_frame, text="Generate Schedule", command=self.run_scheduler)
        self.schedule_button.pack(pady=5)
        
        self.tab_view = ctk.CTkTabview(self.schedule_frame)
        self.tab_view.pack(padx=10, pady=10, fill="both", expand=True)

        self.edf_tab = self.tab_view.add("EDF Schedule")
        self.static_edf_tab = self.tab_view.add("Static EDF")
        self.cycle_conserving_tab = self.tab_view.add("Cycle-Conserving DVS EDF")

        self.init_schedule_tables()

    def update_viewed_settings_display(self):
        self.viewed_settings_display = ctk.CTkLabel(
            self.left_frame, 
            text=(
                f"Simulation Duration: {config.SIMULATION_DURATION_SECONDS} s\n"
                f"Ticks/Second: {config.TICKS_PER_SECOND}\n"
                f"Time Quantum: {config.TIME_QUANTUM} s\n"
                f"Idle Power: {config.IDLE_POWER} W\n"
                f"CC-EDF Min %: {config.CC_EDF_EXECUTION_TIME_RANGE['min_percent']}%\n"
                f"CC-EDF Max %: {config.CC_EDF_EXECUTION_TIME_RANGE['max_percent']}%"
            ),
            justify="left"
        )
        self.viewed_settings_display.grid(row=6, column=0, pady=(0, 5))

    def apply_settings(self):
        try:
            # Update simulation duration in seconds
            if self.sim_duration_entry.get():
                new_duration = float(self.sim_duration_entry.get())
                config.SIMULATION_DURATION_SECONDS = new_duration
                config.SIMULATION_DURATION_TICKS = int(config.SIMULATION_DURATION_SECONDS * config.TICKS_PER_SECOND)

            # Update time quantum
            if self.time_quantum_entry.get():
                new_tq = float(self.time_quantum_entry.get())
                config.TIME_QUANTUM = new_tq
                # Recompute dependent values
                config.TICKS_PER_SECOND = int(round(1 / config.TIME_QUANTUM))
                config.SIMULATION_DURATION_TICKS = int(config.SIMULATION_DURATION_SECONDS * config.TICKS_PER_SECOND)

            # Update idle power
            if self.idle_power_entry.get():
                config.IDLE_POWER = float(self.idle_power_entry.get())

            # Update CC-EDF execution time range
            if self.cc_min_entry.get():
                config.CC_EDF_EXECUTION_TIME_RANGE['min_percent'] = int(self.cc_min_entry.get())
            if self.cc_max_entry.get():
                config.CC_EDF_EXECUTION_TIME_RANGE['max_percent'] = int(self.cc_max_entry.get())

            self.update_viewed_settings_display()
            self.show_info("Configuration settings updated successfully!")
        except ValueError:
            self.show_error("Invalid input! Please enter valid numeric values for the settings.")

    def refresh_frequency_listbox(self):
        self.freq_listbox.delete(0, "end")  
        for freq, power in config.AVAILABLE_FREQUENCIES.items():
            self.freq_listbox.insert("end", f"{freq} GHz: {power} W")

    def remove_frequency(self):
        try:
            selected_index = self.freq_listbox.curselection()
            if not selected_index:
                self.show_error("Please select a frequency to remove.")
                return

            selected_text = self.freq_listbox.get(selected_index)
            freq = float(selected_text.split(" ")[0])
            del config.AVAILABLE_FREQUENCIES[freq]

            self.show_info(f"Removed frequency {freq} GHz.")
            self.refresh_frequency_listbox()
        except Exception as e:
            self.show_error(f"Error removing frequency: {e}")

    def add_task(self):
        try:
            period_sec = float(self.period_entry.get())
            execution_time_sec = float(self.execution_entry.get())
            task_name = f"Task{len(self.tasks) + 1}"
            task = {"name": task_name, "execution_time_sec": execution_time_sec, "period_sec": period_sec}
            self.tasks.append(task)
            self.task_listbox.insert("end", f"{task_name}: Period={period_sec}s, Execution Time={execution_time_sec}s")
            self.period_entry.delete(0, "end")
            self.execution_entry.delete(0, "end")
            util = calculate_utilization(self.tasks) * 100
            self.utilization_label.configure(text=f"Task Set Utilization: {util:.2f}%")
        except ValueError:
            self.show_error("Invalid input! Please enter numeric values for Period and Execution Time.")

    def delete_task(self):
        try:
            selected_index = self.task_listbox.curselection()
            if not selected_index:
                self.show_error("Please select a task to delete.")
                return
            
            self.tasks.pop(selected_index[0])
            self.task_listbox.delete(selected_index)

            self.show_info("Task deleted successfully!")
            util = calculate_utilization(self.tasks) * 100
            self.utilization_label.configure(text=f"Task Set Utilization: {util:.2f}%")
        except Exception as e:
            self.show_error(f"Error while deleting task: {str(e)}")

    def add_frequency(self):
        try:
            new_freq = float(self.new_freq_entry.get())
            new_power = float(self.new_power_entry.get())
            
            config.AVAILABLE_FREQUENCIES[new_freq] = new_power
            self.show_info(f"Added/Updated frequency {new_freq} GHz with power {new_power} W.")
            
            self.refresh_frequency_listbox()

            self.new_freq_entry.delete(0, "end")
            self.new_power_entry.delete(0, "end")
        except ValueError:
            self.show_error("Invalid input! Please enter valid numbers for Frequency and Power.")

    def run_scheduler(self):
        util = calculate_utilization(self.tasks) * 100
        self.utilization_label.configure(text=f"Task Set Utilization: {util:.2f}%")

        # Clear previous table entries
        for row in self.edf_table.get_children():
            self.edf_table.delete(row)
        for row in self.static_edf_table.get_children():
            self.static_edf_table.delete(row)
        for row in self.cc_edf_table.get_children():
            self.cc_edf_table.delete(row)

        tasks_edf = copy.deepcopy(self.tasks)
        tasks_static = copy.deepcopy(self.tasks)
        tasks_cc = copy.deepcopy(self.tasks)

        # Basic EDF: Run with max frequency
        frequency = config.MAX_FREQUENCY
        power = config.AVAILABLE_FREQUENCIES[frequency]
        self.run_and_display_schedule(tasks_edf, frequency, power, self.edf_table, "Basic EDF")

        # Static EDF: Derive static frequency from utilization (like main.py's get_static_frequency logic)
        # We'll replicate the logic from main.get_static_frequency here:
        from main import get_static_frequency
        static_freq, static_power = get_static_frequency(tasks_static)
        self.run_and_display_schedule(tasks_static, static_freq, static_power, self.static_edf_table, "Static EDF")

        # CC-EDF
        safe_frequency = static_freq if (sum((t["execution_time_sec"]/t["period_sec"]) for t in tasks_cc) <= 1) else config.MAX_FREQUENCY
        self.run_and_display_cc_schedule(tasks_cc, safe_frequency, self.cc_edf_table, "Cycle-Conserving EDF")

    def run_and_display_schedule(self, tasks_info, frequency, power, table, description):
        # Similar to simulate_schedule in main.py but display in the table
        scheduler = EDFScheduler()
        from main import init_tasks
        tasks = init_tasks(tasks_info, frequency, power, (100,100))
        for task in tasks:
            scheduler.add_periodic_task(task)

        idle_ticks = 0
        total_energy = 0

        while scheduler.current_ticks < config.SIMULATION_DURATION_TICKS:
            scheduler.handle_arrivals()
            scheduler.check_deadline_misses()

            current_time_sec = scheduler.current_ticks / config.TICKS_PER_SECOND

            if scheduler.currently_running_task:
                next_task = scheduler.currently_running_task
            else:
                next_task = scheduler.schedule()

            if next_task:
                deadline_sec = next_task.deadline_ticks / config.TICKS_PER_SECOND
                completed = next_task.execute(1, frequency)
                energy = power * config.TIME_QUANTUM
                total_energy += energy
                table.insert("", "end", values=(f"{current_time_sec:.2f}s", next_task.name, f"{deadline_sec:.2f}s"))
                if completed:
                    next_task.reset(100,100)
                    scheduler.add_periodic_task(next_task)
                    scheduler.currently_running_task = None
                else:
                    scheduler.currently_running_task = next_task
            else:
                # Idle
                idle_ticks += 1
                idle_energy = config.IDLE_POWER * config.TIME_QUANTUM
                total_energy += idle_energy
                table.insert("", "end", values=(f"{current_time_sec:.2f}s", "Idle", "N/A"))

            scheduler.advance_time(1)

        # Add summary row
        idle_time = idle_ticks * config.TIME_QUANTUM
        table.insert("", "end", values=("", f"Idle Time: {idle_time:.2f}s", f"Missed: {scheduler.missed_deadlines}"))

    def run_and_display_cc_schedule(self, tasks_info, safe_frequency, table, description):
        # Similar to simulate_cc_edf in main.py but display in the table
        scheduler = CC_EDFScheduler(safe_frequency)
        rng = config.CC_EDF_EXECUTION_TIME_RANGE
        from main import init_tasks
        tasks = init_tasks(tasks_info, config.MAX_FREQUENCY, config.MAX_POWER, (rng["min_percent"], rng["max_percent"]))
        for t in tasks:
            scheduler.add_periodic_task(t)

        idle_ticks = 0
        total_energy = 0

        while scheduler.current_ticks < config.SIMULATION_DURATION_TICKS:
            scheduler.handle_arrivals()
            scheduler.check_deadline_misses()

            current_time_sec = scheduler.current_ticks / config.TICKS_PER_SECOND

            current_frequency, current_power = scheduler.adjust_frequency()

            if scheduler.currently_running_task:
                next_task = scheduler.currently_running_task
            else:
                next_task = scheduler.schedule()

            if next_task:
                deadline_sec = next_task.deadline_ticks / config.TICKS_PER_SECOND
                completed = next_task.execute(1, current_frequency)
                energy = current_power * config.TIME_QUANTUM
                total_energy += energy
                table.insert("", "end", values=(f"{current_time_sec:.2f}s", next_task.name, f"{current_frequency:.2f}GHz", f"{deadline_sec:.2f}s"))
                if completed:
                    if next_task.actual_execution_ticks < next_task.worst_case_execution_ticks:
                        scheduler.slack_observed = True
                    next_task.reset(rng["min_percent"], rng["max_percent"])
                    scheduler.add_periodic_task(next_task)
                    scheduler.currently_running_task = None
                else:
                    scheduler.currently_running_task = next_task
            else:
                # Idle
                idle_ticks += 1
                idle_energy = config.IDLE_POWER * config.TIME_QUANTUM
                total_energy += idle_energy
                table.insert("", "end", values=(f"{current_time_sec:.2f}s", "Idle", f"{current_frequency:.2f}GHz", "N/A"))

            scheduler.advance_time(1)

        idle_time = idle_ticks * config.TIME_QUANTUM
        table.insert("", "end", values=("", f"Idle Time: {idle_time:.2f}s", "", f"Missed: {scheduler.missed_deadlines}"))

    def init_schedule_tables(self):
        # Table in EDF Tab
        self.edf_table = ttk.Treeview(self.edf_tab, columns=("Time", "Task", "Deadline"), show="headings", height=15)
        self.edf_table.heading("Time", text="Time")
        self.edf_table.heading("Task", text="Task")
        self.edf_table.heading("Deadline", text="Deadline")
        self.edf_table.pack(padx=5, pady=5, fill="both", expand=True)

        # Table in Static EDF Tab
        self.static_edf_table = ttk.Treeview(self.static_edf_tab, columns=("Time", "Task", "Deadline"), show="headings", height=15)
        self.static_edf_table.heading("Time", text="Time")
        self.static_edf_table.heading("Task", text="Task")
        self.static_edf_table.heading("Deadline", text="Deadline")
        self.static_edf_table.pack(padx=5, pady=5, fill="both", expand=True)

        # Table in Cycle-Conserving DVS EDF Tab
        self.cc_edf_table = ttk.Treeview(self.cycle_conserving_tab, columns=("Time", "Task", "Frequency", "Deadline"), show="headings", height=15)
        self.cc_edf_table.heading("Time", text="Time")
        self.cc_edf_table.heading("Task", text="Task")
        self.cc_edf_table.heading("Frequency", text="Frequency (GHz)")
        self.cc_edf_table.heading("Deadline", text="Deadline")
        self.cc_edf_table.pack(padx=5, pady=5, fill="both", expand=True)

    def show_info(self, message):
        info_window = ctk.CTkToplevel(self)
        info_window.title("Info")
        ctk.CTkLabel(info_window, text=message).pack(padx=20, pady=20)
        ctk.CTkButton(info_window, text="OK", command=info_window.destroy).pack(pady=10)

    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        ctk.CTkLabel(error_window, text=message).pack(padx=20, pady=20)
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)


if __name__ == "__main__":
    app = SchedulerGUI()
    app.mainloop()
