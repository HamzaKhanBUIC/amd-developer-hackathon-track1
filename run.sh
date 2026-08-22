#!/bin/bash
# run.sh - Defensive wrapper for AMD Hackathon Grading
# Forwards all CLI arguments directly to the python script

# Ensure python exits properly on error
set -e

python agent.py "$@"
