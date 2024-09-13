.PHONY: help shell simulator tangle untangle lint format test clean package-files install-deps init setup

PYTHON_FILES := $(shell find . -name "*.py")
TMP_PROMPT_DIR := $(shell mktemp -d)
TMP_DIR := $(shell mktemp -d)

# Display help information
help:
	@echo "Available targets:"
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^# (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 2, RLENGTH); \
			printf "\033[36m%-30s\033[0m %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

# Activate poetry shell
shell:
	poetry shell

# Install the project in editable mode
install:
	pip install -e .

# Run the flow simulator
simulator:
	python -m flow_simulator.main

# Tangle org-mode files
tangle:
	@echo "Tangling README.org..."
	@emacs --batch \
		--eval "(require 'org)" \
		--eval "(org-babel-tangle-file \"README.org\")"
	@echo "Tangling complete."

# Untangle generated files
untangle:
	@echo "Untangling amazon-bedrock-prompt-evaluation..."
	@for file in *.py *.sh *.json *.tmpl; do \
		if [ -f "$$file" ]; then \
			echo "Processing $$file..."; \
			mv "$$file" "$$file.bak"; \
			awk '/^#\+begin_src/ {p=1; next} /^#\+end_src/ {p=0; next} p' "$$file.bak" > "$$file"; \
			rm "$$file.bak"; \
		fi; \
	done
	@echo "Untangling complete."

# Collect flow simulator files
files-to-prompt:
	@echo Collecting the flow simulator
	files-to-prompt flow_simulator | tee $(TMP_PROMPT_DIR)/flow_simulator_files.txt
	@echo "See $(TMP_PROMPT_DIR)/flow_simulator_files.txt"

# Run linting
lint:
	poetry run flake8 $(PYTHON_FILES)
	poetry run mypy $(PYTHON_FILES)

# Format code
format:
	poetry run black $(PYTHON_FILES)
	poetry run isort $(PYTHON_FILES)

# Run tests
test:
	poetry run pytest flow_simulator/tests test_evaluation_flow.py

# Clean up generated files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .mypy_cache .pytest_cache

# Package files for prompting
package-files:
	@echo "Packaging files to $(TMP_DIR)"
	@mkdir -p $(TMP_DIR)/prompts
	@cp -R prompts/* $(TMP_DIR)/prompts/
	@cp prompts_dataset.jsonl $(TMP_DIR)/
	@cp test_evaluation_flow.py $(TMP_DIR)/
	@cp evaluate_prompts_at_scale.py $(TMP_DIR)/
	@cp cleanup_resources.py $(TMP_DIR)/
	@poetry run files-to-prompt $(TMP_DIR) -o $(TMP_DIR)/all_files_content.txt
	@echo "Files packaged and content generated at $(TMP_DIR)/all_files_content.txt"
	@echo "To clean up, run: rm -rf $(TMP_DIR)"

# Install project dependencies
install-deps:
	poetry add files-to-prompt flake8 mypy black isort pytest

# Run all main tasks
all: shell lint format test

# Initialize the project
init:
	@if [ ! -f pyproject.toml ]; then \
		poetry init -n; \
		echo "Poetry project initialized."; \
	else \
		echo "Poetry project already initialized."; \
	fi

# Set up the project
setup: init install-deps
	@echo "Project setup complete."

# Check if the project is set up correctly
check-setup:
	@if [ ! -f pyproject.toml ]; then \
		echo "Project not initialized. Run 'make init' first."; \
		exit 1; \
	fi
	@if ! poetry show | grep -q "files-to-prompt"; then \
		echo "Dependencies not installed. Run 'make install-deps' first."; \
		exit 1; \
	fi
	@echo "Project is set up correctly."
