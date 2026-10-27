#!/usr/bin/env bash
set -euo pipefail
GOOSE="${1:-goose}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/build/goose-generated"
mkdir -p "$OUT"
"$GOOSE" -o "$OUT/hello.c" "$ROOT/experiments/hello.goose"
"$GOOSE" --emit-runtime "$OUT/goose_runtime.c"
echo "Generated C in $OUT (NOT yet ESP32-compatible)"
