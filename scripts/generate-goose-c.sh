#!/usr/bin/env bash
set -euo pipefail
GOOSE="${1:-${GOOSE_BIN:-goose}}"
if ! command -v "$GOOSE" &>/dev/null && [ -f "$HOME/.gemini/antigravity/scratch/goose/build/goose" ]; then
    GOOSE="$HOME/.gemini/antigravity/scratch/goose/build/goose"
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/build/goose-generated"
mkdir -p "$OUT"
"$GOOSE" -o "$OUT/hello.c" "$ROOT/experiments/hello.goose"
"$GOOSE" -O0 -o "$OUT/array_scan.c" "$ROOT/benchmarks/goose/array_scan.goose"
"$GOOSE" --emit-runtime "$OUT/goose_runtime.c"
echo "Generated C in $OUT"
