@echo off
for /L %%a in (1,1,254) do @start /b ping 192.168.1.%%a -w 100 -n 2 > NUL
@echo on
timeout 5
cls
Rem arp -a | find "b8-27-eb-72-1f-1e"
for /F "tokens=1,2,3" %%A in ('"arp -a | find "b8-27-eb-72-1f-1e""') DO (SET piip=%%A)
echo %piip%