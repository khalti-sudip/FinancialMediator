# Makefile for FinancialMediator operations

.PHONY: all setup-dev deploy-k8s generate-manifests

all: setup-dev deploy-k8s

setup-dev:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	./scripts/setup-dev-env.sh

deploy-k8s:
	./scripts/deploy-k8s.sh

generate-manifests:
	python scripts/generate_k8s_manifests.py

clean:
	rm -rf venv
	rm -rf __pycache__
	rm -rf *.pyc

test:
	python -m pytest tests/
