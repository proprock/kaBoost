#!/usr/bin/env bash
# Materialize the frozen pilot project in the empty workspace.
# The source repository and commit are filled in by tests/behavior/run_plugin_eval.py in a temporary copy.
set -euo pipefail
git -C '@SOURCE@' archive '@COMMIT@' | tar -x -C .
