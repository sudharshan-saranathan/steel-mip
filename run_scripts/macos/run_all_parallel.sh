#!/usr/bin/env bash
#
# run_all_parallel.sh (macOS)
#
# Launches all four NG cases concurrently, each running the full
# (scenario x h2end x year x ccs x scrap) sweep via run_one_ng.sh.
# Each case's console output is redirected to log_NG_<NG>.out (in the project
# root) so the parallel streams don't interleave.
#
# Usage:   ./run_all_parallel.sh
#
# Configuration (override by exporting before calling):
#   AMPL_EXE  path to the ampl executable (passed through to run_one_ng.sh)
#   SCENARIOS scenarios to run            (passed through to run_one_ng.sh)
#   NG_CASES  space-separated NG values   (default: "5 10 15 20")

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"

NG_CASES="${NG_CASES:-5 10 15 20}"

echo "Running NG cases in parallel: ${NG_CASES}"

pids=()
for NG in ${NG_CASES}; do
  "$SCRIPT_DIR/run_one_ng.sh" "${NG}" > "log_NG_${NG}.out" 2>&1 &
  pids+=("$!")
  echo "  launched NG=${NG} (pid $!) -> log_NG_${NG}.out"
done

echo "All jobs launched. Waiting for completion..."

fail=0
for pid in "${pids[@]}"; do
  if ! wait "${pid}"; then
    echo "  WARNING: job pid ${pid} exited non-zero"
    fail=1
  fi
done

if [[ "${fail}" -eq 0 ]]; then
  echo "All jobs finished successfully."
else
  echo "All jobs finished, but one or more reported errors (see log_NG_*.out)."
fi
