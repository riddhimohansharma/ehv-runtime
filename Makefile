.PHONY: unit_test demo test all clean

unit_test:
	PYTHONPATH=. pytest tests/

demo:
	python3 examples/clinical_dosage.py
	python3 examples/latency_bench.py

test:
	python3 experiments/crdt_convergence.py
	python3 experiments/epoch_staleness.py
	python3 experiments/gbom_audit.py

all: unit_test demo test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
