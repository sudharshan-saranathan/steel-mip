@echo off
setlocal enabledelayedexpansion

set NG=%1
set "AMPL_EXE=C:\Users\Energ Lab\AMPL\ampl.exe"
set "WORKDIR=C:\Nakul\AMPL"

cd /d "%WORKDIR%"

mkdir results\NG_%NG% 2>nul

echo Running NG = %NG%

set TEMPFILE=temp_%NG%.mod

for %%A in (1000 1500 2000 2500 3000 3500 4000) do (
for %%B in (2030 2033 2036 2039 2042 2045) do (
for %%C in (25 50 75 100 125) do (
for %%D in (0.04 0.05 0.06 0.07 0.08) do (

```
            set LABEL=h2end%%A_yr%%B_ccs%%C_scrap%%D
            set OUTFILE=results\NG_%NG%\!LABEL!.txt

            echo Running !LABEL!

            copy template.mod !TEMPFILE! > nul

            powershell -Command "(Get-Content !TEMPFILE!) -replace 'NGVAL','%NG%' -replace 'H2ENDVAL','%%A' -replace 'H2YEARVAL','%%B' -replace 'CCSVAL','%%C' -replace 'SCRAPVAL','%%D' | Set-Content !TEMPFILE!"

            "%AMPL_EXE%" !TEMPFILE! > "!OUTFILE!" 2>&1

        )
    )
)
```

)

echo DONE NG = %NG%
