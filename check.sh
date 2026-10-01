#!/bin/sh
# Run before every push; CI runs it too. Every skill must install with the skills CLI, every
# script with a --self-test must pass it, and the files the two video skills share must match.
set -u
cd "$(dirname "$0")"
fail=0
if command -v uv >/dev/null 2>&1; then PY="uv run -q --with numpy --with scipy python"; else PY=python3; fi
for f in */scripts/*.py; do
  grep -q -- '--self-test' "$f" || continue
  $PY "$f" --self-test >/dev/null 2>&1 || { echo "FAIL self-test: $f"; fail=1; }
done
for f in scripts/music.py scripts/direction.py history/seed.jsonl references/direction.md references/arcs.md references/brand.md; do
  cmp -s "app-launch-video/$f" "motion-reel/$f" || { echo "FAIL: $f differs between app-launch-video and motion-reel; change both"; fail=1; }
done
want=$(ls -d */SKILL.md | wc -l | tr -d ' ')
out=$(NO_COLOR=1 npx -y skills add . -l </dev/null 2>&1)
if echo "$out" | grep 'Skipped'; then fail=1; fi
if ! echo "$out" | grep -q "Found $want skills"; then
  echo "FAIL: the skills CLI did not find all $want skills"
  fail=1
fi
[ "$fail" -eq 0 ] && echo "check OK: $want skills install, all self-tests pass, shared files match"
exit "$fail"
