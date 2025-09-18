#!/bin/bash

# Exit on error
set -e

# --- GradingAgentAPI tests ---
echo "Running GradingAgentAPI tests..."
export DATABASE_URL='sqlite:///./test.db'
export PYTHONPATH=$PYTHONPATH:/Users/ryancaudill/Desktop/Projects/Grader/GradingAgentAPI
source GradingAgentAPI/venv/bin/activate
pip install -r GradingAgentAPI/requirements.txt
python -m pytest GradingAgentAPI/tests/
deactivate

# --- GradingAgentFrontend tests ---
echo "Running GradingAgentFrontend tests..."
source GradingAgentFrontend/venv/bin/activate
pip install -r GradingAgentFrontend/requirements.txt
python GradingAgentFrontend/manage.py test AgentDeployer
deactivate

echo "All tests passed!"
