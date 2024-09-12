.PHONY: tangle

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
