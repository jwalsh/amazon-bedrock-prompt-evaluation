.PHONY: shell simulator tangle untangle lint format test clean package-files install-deps

PYTHON_FILES := $(shell find . -name "*.py")

shell:
	poetry shell

simulator:
	python -m flow_simulator.main

tangle:
	@echo "Tangling README.org..."
	@emacs --batch \
		--eval "(require 'org)" \
		--eval "(org-babel-tangle-file \"README.org\")"
	@echo "Tangling complete."

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

TMP_PROMPT_DIR := $(shell mktemp -d)

files-to-prompt:
	@echo Collecting the flow simulator
	files-to-prompt flow_simulator | tee $(TMP_PROMPT_DIR)/flow_simulator_files.txt
	@echo "See $(TMP_PROMPT_DIR)/flow_simulator_files.txt"

lint:
	poetry run flake8 $(PYTHON_FILES)
	poetry run mypy $(PYTHON_FILES)

format:
	poetry run black $(PYTHON_FILES)
	poetry run isort $(PYTHON_FILES)

test:
	poetry run pytest

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .mypy_cache .pytest_cache

TMP_DIR := $(shell mktemp -d)

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

install-deps:
	poetry add files-to-prompt flake8 mypy black isort pytest

all: shell lint format test
