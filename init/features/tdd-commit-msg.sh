#!/bin/sh
# Checks TDD red/green commit messages (kaBoost tdd-commit-hook); other commits pass. Without Python or the
# script the commit goes through with a warning. The script sits next to this hook, not in the working tree, so a
# checked-out branch cannot change what runs on commit.
script="$(dirname "$0")/kaboost_tdd_commit_msg.py"
if [ ! -f "$script" ]; then
  echo "kaboost tdd-commit-hook: $script not found; message not checked" >&2
  exit 0
fi
if command -v py >/dev/null 2>&1 && py -3 -c '' >/dev/null 2>&1; then
  exec py -3 "$script" "$1"
fi
for python in python3 python; do
  if command -v "$python" >/dev/null 2>&1 && "$python" -c '' >/dev/null 2>&1; then
    exec "$python" "$script" "$1"
  fi
done
echo "kaboost tdd-commit-hook: no Python found; message not checked" >&2
exit 0
