@echo off
setlocal enabledelayedexpansion
echo ============================================================
echo   LoD Agent SDK — Game Server Setup (Windows)
echo ============================================================
echo.

:: Check .NET SDK
where dotnet >nul 2>nul
if !errorlevel! neq 0 (
    echo ERROR: .NET SDK not found. Install from https://dotnet.microsoft.com/download
    echo        Recommended: .NET SDK 8.0
    goto :error
)
echo [OK] .NET SDK found
dotnet --version

:: Check Redis
where redis-server >nul 2>nul
if !errorlevel! neq 0 (
    echo.
    echo WARNING: Redis not found in PATH.
    echo          Download from https://github.com/microsoftarchive/redis/releases
    echo          Or install via: winget install Redis.Redis
    echo          Redis is REQUIRED for the agent SDK to communicate with the server.
    echo.
)

:: Check Git
where git >nul 2>nul
if !errorlevel! neq 0 (
    echo ERROR: Git not found. Install from https://git-scm.com/downloads
    goto :error
)
echo [OK] Git found

:: Clone GameServer if not present
if not exist "GameServer" (
    echo.
    echo Cloning LoD Agent GameServer...
    git clone https://github.com/MiscellaneousStuff/LeagueSandbox-RL-Learning GameServer
    cd GameServer
    git checkout master
    git submodule init
    git submodule update
    cd ..
) else (
    echo [OK] GameServer already cloned
)

:: Update .NET target framework to net8.0
echo.
echo Updating project targets to net8.0...
powershell -Command "Get-ChildItem -Path GameServer -Recurse -Filter *.csproj | ForEach-Object { (Get-Content $_.FullName) -replace 'netcoreapp3\.[0-9]', 'net8.0' | Set-Content $_.FullName }"

:: Build
echo.
echo Building GameServer...
cd GameServer
dotnet restore .
if !errorlevel! neq 0 goto :error
dotnet build .
if !errorlevel! neq 0 goto :error
cd ..

:: Write config
echo.
echo Writing config_dirs.txt...
echo [dirs]> config_dirs.txt
echo gameserver = ./GameServer/GameServerConsole/bin/Debug/net8.0/>> config_dirs.txt
echo lolclient = >> config_dirs.txt

echo.
echo ============================================================
echo   Setup complete!
echo.
echo   Next steps:
echo     1. Start Redis:    redis-server
echo     2. Run an agent:   python examples/my_first_agent.py
echo ============================================================
goto :eof

:error
echo.
echo ============================================================
echo   Setup FAILED. Check the errors above.
echo ============================================================
exit /b 1
