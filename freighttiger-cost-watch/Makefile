.PHONY: install test run eval

install:
	pip install -r requirements.txt

test:
	python src/costwatch/formatcheck.py

run:
	python scripts/run_pipeline.py
	python src/costwatch/formatcheck.py

eval:
	echo "Eval harness coming soon..."
