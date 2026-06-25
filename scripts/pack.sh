#!/usr/bin/env bash
# Pack a CLEAN coded-agent .nupkg.
#
# `uip codedagent pack` bundles the whole project tree and ignores .gitignore /
# .uipathignore — so it sweeps in node_modules, the video renders, graphify-out,
# etc. (it does exclude .env). This stashes the heavy/irrelevant dirs on the same
# filesystem (instant mv), packs, and restores them — yielding a ~200 KB package
# of just main.py + costguard/ + pyproject + uipath.json.
#
#   bash scripts/pack.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

STASH="../_packstash_$$"
HEAVY=(video graphify-out .agents node_modules docs tests)

mkdir -p "$STASH"
moved=()
for d in "${HEAVY[@]}"; do
  if [ -e "$d" ]; then mv "$d" "$STASH"/ && moved+=("$d"); fi
done

restore() { for d in "${moved[@]}"; do mv "$STASH/$d" .; done; rmdir "$STASH" 2>/dev/null || true; }
trap restore EXIT

uip codedagent pack
echo "Packed: $(ls -1 .uipath/*.nupkg | tail -1)"
