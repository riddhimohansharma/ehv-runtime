.PHONY: unit_test demo gcd_demo test bench all clean

unit_test:
	PYTHONPATH=. pytest tests/

demo:
	python3 examples/clinical_dosage.py
	python3 examples/latency_bench.py

gcd_demo:
	python3 examples/gcd_dosage.py

test:
	python3 experiments/crdt_convergence.py
	python3 experiments/epoch_staleness.py
	python3 experiments/gbom_audit.py

bench:
	PYTHONPATH=. python3 bench/sev_snp_benchmark.py
	PYTHONPATH=. python3 bench/measure_enforcement.py

all: unit_test demo gcd_demo test bench

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
