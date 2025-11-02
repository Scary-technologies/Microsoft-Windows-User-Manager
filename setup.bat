@echo off
chcp 65001 >nul
color 0A
title Advanced Windows Control Panel Installer

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║          🛡️  Advanced Windows Management Control Panel  🛡️      ║
echo ║                     Automatic Installation Script             ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo [1/5] Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed!
    echo.
    echo Please download and install Python 3.8 or higher from the link below:
    echo https://www.python.org/downloads/
    echo.
    echo Note: Make sure to enable "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo ✅ Python is installed
python --version

REM Check pip
echo.
echo [2/5] Checking for pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not installed!
    echo Installing pip...
    python -m ensurepip --default-pip
)
echo ✅ pip is ready
pip --version

REM Upgrade pip
echo.
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  Error while upgrading pip, continuing anyway...
)

REM Install dependencies
echo.
echo [4/5] Installing required libraries...
echo This step may take a few minutes...
echo.

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error installing dependencies!
    echo.
    echo Try running the following commands manually:
    echo.
    echo pip install customtkinter
    echo pip install psutil
    echo pip install wmi
    echo pip install matplotlib
    echo pip install pillow
    echo pip install requests
    echo pip install pywin32
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ All dependencies were installed successfully!

REM Check for main file
echo.
echo [5/5] Checking for the main program file...
if not exist "windows_control_panel.py" (
    echo ❌ File windows_control_panel.py not found!
    echo Please make sure the file is in the same folder.
    pause
    exit /b 1
)
echo ✅ Main program file found

REM Create Desktop Shortcut
echo.
echo Would you like to create a shortcut on your Desktop? (Y/N)
set /p create_shortcut=
if /i "%create_shortcut%"=="Y" (
    echo Creating shortcut...
    
    set SCRIPT_DIR=%~dp0
    set DESKTOP=%USERPROFILE%\Desktop
    
    echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
    echo sLinkFile = "%DESKTOP%\Windows Control Panel.lnk" >> CreateShortcut.vbs
    echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
    echo oLink.TargetPath = "python.exe" >> CreateShortcut.vbs
    echo oLink.Arguments = """%SCRIPT_DIR%windows_control_panel.py""" >> CreateShortcut.vbs
    echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
    echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,47" >> CreateShortcut.vbs
    echo oLink.Description = "Advanced Windows Control Panel" >> CreateShortcut.vbs
    echo oLink.Save >> CreateShortcut.vbs
    
    cscript CreateShortcut.vbs >nul
    del CreateShortcut.vbs
    
    echo ✅ Shortcut created on Desktop
)

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                    ✅ Installation completed successfully! ✅   ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo To run the program:
echo.
echo 1. Double-click on windows_control_panel.py
echo 2. Or run the following command in Command Prompt:
echo    python windows_control_panel.py
echo.
echo ⚠️  Note: For full functionality, run the program as Administrator
echo    (Right-click the file and choose "Run as administrator")
echo.
echo Would you like to run the program now? (Y/N)
set /p run_now=
if /i "%run_now%"=="Y" (
    echo.
    echo Launching program...
    start "" python windows_control_panel.py
)

echo.
echo For more information, read the README.md file.
echo.
pause
