echo all: %*
IF "%1"=="" EXIT /b
for /f "tokens=1,* delims= " %%a in ("%*") do set ALL_BUT_FIRST=%%b
ssh ms@%1% -i .ssh\pi "cd smacz/rejestrator; ./eksportuj -c -e -l 2>/dev/null" 