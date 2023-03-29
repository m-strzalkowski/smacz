echo all: %*
IF "%1"=="" EXIT /b
for /f "tokens=1,* delims= " %%a in ("%*") do set ALL_BUT_FIRST=%%b
ssh ms@%piip% -i .ssh\pi "cd smacz/rejestrator; ./eksportuj" >importowane\%1.csv