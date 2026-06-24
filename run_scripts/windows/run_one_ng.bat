@echo off
setlocal enabledelayedexpansion
rem ============================================================================
rem run_one_ng.bat (Windows) -- runs the full scenario sweep for a single NG.
rem
rem For one NG (cost) value, loops over the NG-availability scenarios and, within
rem each, the (h2end x year x ccs x scrap) grid. Substitutes the placeholder
rem tokens in template.mod (including the scenario include file), runs AMPL, and
rem writes output to  results\NG_<NG>\<scenario>\<label>.txt
rem
rem This script lives in run_scripts\windows\ ; the model files (template.mod,
rem modules\, scenarios\, results\) live two levels up at the project root.
rem
rem Usage:   run_one_ng.bat <NG>
rem Example: run_one_ng.bat 5
rem
rem Override before calling:
rem   set AMPL_EXE=C:\path\to\ampl.exe   (default: ampl.exe, found on PATH)
rem   set SCENARIOS=normal               (default: "normal shock optimistic")
rem
rem NOTE: AMPL must be able to find the gurobi solver. With the pip AMPL modules,
rem put ...\ampl_module_gurobi\bin on PATH (it holds gurobi.exe).
rem ============================================================================

if "%~1"=="" ( echo usage: run_one_ng.bat ^<NG^> & exit /b 1 )
set "NG=%~1"

rem Project root = two levels up from this script's directory (%~dp0).
pushd "%~dp0..\.." || ( echo ERROR: cannot cd to project root & exit /b 1 )

if not defined AMPL_EXE set "AMPL_EXE=ampl.exe"
if not defined SCENARIOS set "SCENARIOS=normal shock optimistic"

set "TEMPFILE=temp_%NG%.mod"

for %%S in (%SCENARIOS%) do (
    call :scenfile %%S SFILE
    if "!SFILE!"=="" ( echo ERROR: unknown scenario '%%S' & popd & exit /b 1 )
    if not exist "!SFILE!" ( echo ERROR: scenario file not found: !SFILE! & popd & exit /b 1 )

    if not exist "results\NG_%NG%\%%S" mkdir "results\NG_%NG%\%%S"
    echo === NG=%NG% scenario=%%S ^(!SFILE!^) ===

    for %%A in (1000 1500 2000 2500 3000 3500 4000) do (
    for %%B in (2030 2033 2036 2039 2042 2045) do (
    for %%C in (25 50 75 100 125) do (
    for %%D in (0.04 0.05 0.06 0.07 0.08) do (
        set "LABEL=h2end%%A_yr%%B_ccs%%C_scrap%%D"
        set "OUTFILE=results\NG_%NG%\%%S\!LABEL!.txt"
        echo Running %%S/!LABEL!
        copy /y template.mod "!TEMPFILE!" >nul
        powershell -NoProfile -Command "(Get-Content '!TEMPFILE!') -replace 'NGVAL','%NG%' -replace 'H2ENDVAL','%%A' -replace 'H2YEARVAL','%%B' -replace 'CCSVAL','%%C' -replace 'SCRAPVAL','%%D' -replace 'NGAVAILFILE','!SFILE!' | Set-Content '!TEMPFILE!'"
        "%AMPL_EXE%" "!TEMPFILE!" > "!OUTFILE!" 2>&1
    ))))
)

del /q "%TEMPFILE%" 2>nul
popd
echo DONE NG = %NG% (scenarios: %SCENARIOS%)
exit /b 0

:scenfile
rem %1 = scenario key, %2 = name of output variable (set to the include path)
if /i "%~1"=="normal"     ( set "%~2=scenarios/ng_avail_normal.mod" & goto :eof )
if /i "%~1"=="shock"      ( set "%~2=scenarios/ng_avail_shock.mod" & goto :eof )
if /i "%~1"=="optimistic" ( set "%~2=scenarios/ng_avail_optimistic.mod" & goto :eof )
set "%~2="
goto :eof
