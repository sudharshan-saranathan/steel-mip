@echo off

echo Running all 4 NG cases in parallel...

start "NG5"  cmd /c run_one_ng.bat 5
start "NG10" cmd /c run_one_ng.bat 10
start "NG15" cmd /c run_one_ng.bat 15
start "NG20" cmd /c run_one_ng.bat 20

echo All jobs launched...
pause