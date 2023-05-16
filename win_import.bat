echo all: %*
IF "%1"=="" EXIT /b
IF "%piip%" == "" win_szukaj.bat
IF "%piip%" == "" EXIT /b
for /f "tokens=1,* delims= " %%a in ("%*") do set ALL_BUT_FIRST=%%b
ssh ms@%piip% -i .ssh\pi "cd smacz/rejestrator; ./eksportuj" >importowane\%1.csv
ECHO "import ended"