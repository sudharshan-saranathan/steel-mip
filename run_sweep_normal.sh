#!/usr/bin/env bash
# Launch the full sweep for the NORMAL NG-availability scenario only
# (4 NG-cost cases x 1,050 grid points = 4,200 runs, 4-way parallel).
cd "$(dirname "$0")"
export SCENARIOS=normal
export AMPL_EXE=/Applications/AMPL/ampl
exec bash run_all_parallel.sh
