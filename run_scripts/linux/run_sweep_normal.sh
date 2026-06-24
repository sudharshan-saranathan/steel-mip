#!/usr/bin/env bash
# Launch the full sweep for the NORMAL NG-availability scenario only
# (4 NG-cost cases x 1,050 grid points = 4,200 runs, 4-way parallel).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export SCENARIOS=normal
export AMPL_EXE="${AMPL_EXE:-ampl}"
exec bash "$SCRIPT_DIR/run_all_parallel.sh"
