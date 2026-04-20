# Makefile para automatizar tareas del proyecto Blacklist API

.PHONY: install test run clean

# Instalar dependencias en el entorno virtual
install:
	python -m venv .venv
	source .venv/bin/activate && pip install -r requirements.txt

# Ejecutar pruebas unitarias con pytest (activando venv)
test: .venv
	source .venv/bin/activate && python -m pytest tests/ -v --tb=short

# Ejecutar la aplicación en modo desarrollo (activando venv)
run: .venv
	source .venv/bin/activate && python application.py