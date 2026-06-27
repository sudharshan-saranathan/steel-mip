#!/usr/bin/env bash
#
# run_one_ng.sh (Linux) — runs the full scenario sweep for a single NG value.
#
# For one NG (cost) value, loops over the requested NG-availability scenarios
# and, within each, the (h2end x year x ccs x scrap) grid. For every combination
# it substitutes the placeholder tokens in template.mod (including the scenario
# include file), runs AMPL, and writes output to
# results/NG_<NG>/<scenario>/<label>.txt
#
# This script lives in run_scripts/linux/ ; the model files (template.mod,
# modules/, scenarios/, results/) live two levels up at the project root, which
# is where everything runs.
#
# Usage:   ./run_one_ng.sh <NG>
# Example: ./run_one_ng.sh 5
#
# Configuration (override by exporting before calling):
#   AMPL_EXE    path to the ampl executable   (default: ampl, i.e. found on PATH)
#   WORKDIR     project root                  (default: two levels up)
#   SCENARIOS   space-separated scenario keys (default: "normal shock optimistic")
#   H2CAPX_VALS override green-H2 capex-multiplier grid (default: 5 values)
#   YEAR_VALS   override year grid            (default: full 6 values)
#   CCS_VALS    override ccs grid             (default: full 5 values)
#   SCRAP_VALS  override scrap grid           (default: full 5 values)

set -euo pipefail

NG="${1:?usage: run_one_ng.sh <NG>}"

AMPL_EXE="${AMPL_EXE:-ampl}"
WORKDIR="${WORKDIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$WORKDIR"

# Scenarios to run (default all three).
SCENARIOS="${SCENARIOS:-normal shock optimistic}"

scen_file() {
  case "$1" in
    normal)     echo "scenarios/ng_avail_normal.mod" ;;
    shock)      echo "scenarios/ng_avail_shock.mod" ;;
    optimistic) echo "scenarios/ng_avail_optimistic.mod" ;;
    *)          echo "" ;;
  esac
}

# Scenario grid (override via env for subset runs)
read -r -a H2CAPX_ARR <<< "${H2CAPX_VALS:-0.5 0.75 1.0 1.25 1.5}"
read -r -a YEAR_ARR  <<< "${YEAR_VALS:-2030 2033 2036 2039 2042 2045}"
read -r -a CCS_ARR   <<< "${CCS_VALS:-25 50 75 100 125}"
read -r -a SCRAP_ARR <<< "${SCRAP_VALS:-0.04 0.05 0.06 0.07 0.08}"

TEMPFILE="temp_${NG}.mod"

for S in ${SCENARIOS}; do
  SFILE="$(scen_file "$S")"
  if [[ -z "${SFILE}" ]]; then
    echo "ERROR: unknown scenario '${S}' (expected: normal shock optimistic)" >&2
    exit 1
  fi
  if [[ ! -f "${SFILE}" ]]; then
    echo "ERROR: scenario file not found: ${SFILE}" >&2
    exit 1
  fi

  mkdir -p "results/NG_${NG}/${S}"
  echo "=== NG=${NG} scenario=${S} (${SFILE}) ==="

  for A in "${H2CAPX_ARR[@]}"; do
    for B in "${YEAR_ARR[@]}"; do
      for C in "${CCS_ARR[@]}"; do
        for D in "${SCRAP_ARR[@]}"; do

          LABEL="h2cx${A}_yr${B}_ccs${C}_scrap${D}"
          OUTFILE="results/NG_${NG}/${S}/${LABEL}.txt"

          echo "Running ${S}/${LABEL}"

          sed \
            -e "s/NGVAL/${NG}/g" \
            -e "s/H2CAPXVAL/${A}/g" \
            -e "s/H2YEARVAL/${B}/g" \
            -e "s/CCSVAL/${C}/g" \
            -e "s/SCRAPVAL/${D}/g" \
            -e "s|NGAVAILFILE|${SFILE}|g" \
            template.mod > "$TEMPFILE"

          "$AMPL_EXE" "$TEMPFILE" > "$OUTFILE" 2>&1

        done
      done
    done
  done
done

rm -f "$TEMPFILE"
echo "DONE NG = ${NG} (scenarios: ${SCENARIOS})"
