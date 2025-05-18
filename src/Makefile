# make setup: Sets up the virtual environment and installs dependencies.
# make run: Runs the main.py file to simulate the EDF scheduler.
# make run-gui: Runs the interface.py file for the graphical interface.
# make clean: Cleans up the virtual environment and generated files.

# Compiler and Flags
PYTHON := python
PIP := pip

# Project Files
MAIN := main.py
INTERFACE := interface.py
CONFIG := config.py
TASK := task.py
EDF := edf.py
SRC := $(MAIN) $(INTERFACE) $(CONFIG) $(TASK) $(EDF)

# Virtual Environment
VENV_DIR := venv
ACTIVATE := $(VENV_DIR)\Scripts\activate.bat
REQUIREMENTS := requirements.txt

# Dependencies
DEPENDENCIES := customtkinter

# Targets
.PHONY: all setup run run-gui clean

all: setup run

setup: $(REQUIREMENTS)
	@echo "Setting up project environment..."
	@$(PYTHON) -m venv $(VENV_DIR)
	@call $(ACTIVATE) && python -m pip install --upgrade pip
	@call $(ACTIVATE) && $(PIP) install $(DEPENDENCIES)
	@echo "Setup complete!"

$(REQUIREMENTS):
	@echo "Generating requirements.txt..."
	@echo $(DEPENDENCIES) > $(REQUIREMENTS)

run:
	@echo "Running Main EDF Simulation..."
	@call $(ACTIVATE) && $(PYTHON) $(MAIN)

run-gui:
	@echo "Running EDF Scheduler GUI..."
	@call $(ACTIVATE) && $(PYTHON) $(INTERFACE)

clean:
	@echo "Cleaning up the project..."
	if exist $(VENV_DIR) rmdir /s /q $(VENV_DIR)
	if exist $(REQUIREMENTS) del $(REQUIREMENTS)
	@echo "Cleanup complete!"

