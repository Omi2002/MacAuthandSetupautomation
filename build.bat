@echo off
REM Builds dist\CBS_V2_Setup.exe  -  run from a NORMAL (non-admin) Command Prompt
REM in the project folder. resources\ must contain both installers + Config_Creator.

echo [1/4] Checking resources...
if not exist "resources\Firefox Setup 50.0.1.exe"        (echo MISSING: Firefox installer & goto :fail)
if not exist "resources\jdk-8u161-windows-i586.exe"      (echo MISSING: JDK installer & goto :fail)
if not exist "resources\Config_Creator\configFileCreator.jar" (echo MISSING: Config_Creator jar & goto :fail)

echo [2/4] Installing build tools...
python -m pip install --quiet pycryptodome pyinstaller || goto :fail

echo [3/4] Cleaning old build...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q CBS_V2_Setup.spec 2>nul

echo [4/4] Building (several minutes - the installers are about 250 MB)...
python -m PyInstaller --onefile --console --uac-admin --add-data "resources;resources" --name CBS_V2_Setup main.py || goto :fail

echo.
echo ===== BUILD OK =====
dir dist\CBS_V2_Setup.exe
echo SHA-256 (publish this next to the exe):
certutil -hashfile dist\CBS_V2_Setup.exe SHA256
pause
exit /b 0

:fail
echo.
echo ===== BUILD FAILED - see the message above =====
pause
exit /b 1
