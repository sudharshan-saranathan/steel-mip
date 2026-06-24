@echo off
rem ============================================================================
rem run_all_parallel.bat (Windows)
rem
rem Launches all four NG cases concurrently, each in its own window, running the
rem full (scenario x h2end x year x ccs x scrap) sweep via run_one_ng.bat.
rem
rem Usage:   run_all_parallel.bat
rem
rem Override before calling (applies to every job):
rem   set AMPL_EXE=C:\path\to\ampl.exe
rem   set SCENARIOS=normal
rem ============================================================================

echo Running all 4 NG cases in parallel...

start "NG5"  cmd /c ""%~dp0run_one_ng.bat" 5"
start "NG10" cmd /c ""%~dp0run_one_ng.bat" 10"
start "NG15" cmd /c ""%~dp0run_one_ng.bat" 15"
start "NG20" cmd /c ""%~dp0run_one_ng.bat" 20"

echo All jobs launched (one window per NG case).
