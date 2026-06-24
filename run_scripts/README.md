# Run scripts

Platform-specific drivers for the parameter sweep. Pick the folder for your OS.
Every script resolves the **project root automatically** (two levels up from the
script) and writes results to `results/` and logs to `log_NG_<NG>.out` at the
root — so you can invoke them from anywhere.

| Folder      | Shell      | AMPL default                | Notes |
|-------------|------------|-----------------------------|-------|
| `windows/`  | cmd `.bat` | `ampl.exe` (on PATH)        | also needs the gurobi solver on PATH (e.g. `...\ampl_module_gurobi\bin`) |
| `macos/`    | bash `.sh` | `/Applications/AMPL/ampl`   | |
| `linux/`    | bash `.sh` | `ampl` (on PATH)            | |

Each folder contains:

- `run_one_ng.{sh,bat} <NG>` — full *scenario × (h2end × year × ccs × scrap)*
  sweep for one NG-cost value → `results/NG_<NG>/<scenario>/<label>.txt`.
- `run_all_parallel.{sh,bat}` — all four NG cases (`5 10 15 20`) concurrently.
- `run_sweep_normal.sh` — the `normal` scenario only, 4-way parallel (unix).

Override defaults with environment variables, e.g.:

```bash
# unix
AMPL_EXE=/opt/ampl/ampl SCENARIOS=normal ./linux/run_one_ng.sh 10
```
```bat
:: windows
set AMPL_EXE=C:\path\to\ampl.exe
set SCENARIOS=normal
run_one_ng.bat 10
```

Other overrides honoured by `run_one_ng`: `SCENARIOS`, `H2END_VALS`, `YEAR_VALS`,
`CCS_VALS`, `SCRAP_VALS` (and `NG_CASES` for `run_all_parallel`).

The Latin-Hypercube Monte-Carlo driver (`monte_carlo.py`) is cross-platform and
lives at the project root.
