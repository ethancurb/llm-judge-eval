#!/bin/bash
# Run all evaluation scripts with API key set

# Read API key from user
read -sp "Enter your OPENAI_API_KEY: " OPENAI_API_KEY
export OPENAI_API_KEY

echo ""
echo "Running semi-objective evaluations..."
echo "======================================"

cd "$(dirname "$0")"

echo ""
echo "1. Running semi-objective baseline & biased evaluations..."
/Users/ethancurb/Documents/Classes/CSCE\ 477/llm-judge-eval/.venv/bin/python semi-obj/run_evals_semi.py

echo ""
echo "2. Running semi-objective bias test..."
/Users/ethancurb/Documents/Classes/CSCE\ 477/llm-judge-eval/.venv/bin/python semi-obj/run_bias_test.py

echo ""
echo "======================================"
echo "All evaluations complete!"
echo "======================================"
