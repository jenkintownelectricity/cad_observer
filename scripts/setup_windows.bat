@echo off
REM ============================================================
REM CAD Observer - Windows Setup Script
REM Run this as Administrator
REM ============================================================

echo.
echo ============================================
echo   CAD Observer Setup
echo ============================================
echo.

REM Create directories
echo Creating directories...
mkdir "C:\CADObserver" 2>nul
mkdir "C:\CADObserver\logs" 2>nul
mkdir "C:\CADObserver\tasks" 2>nul
mkdir "C:\CADObserver\done" 2>nul

echo   Created: C:\CADObserver\
echo   Created: C:\CADObserver\logs\
echo   Created: C:\CADObserver\tasks\
echo   Created: C:\CADObserver\done\
echo.

REM Copy LISP file
echo.
echo Next steps:
echo.
echo 1. Copy 'cad-observer.lsp' to your AutoCAD support folder:
echo    Typical location:
echo    C:\Users\%USERNAME%\AppData\Roaming\Autodesk\AutoCAD [version]\R[xx]\enu\Support\
echo.
echo 2. To auto-load, add this line to acaddoc.lsp:
echo    (load "cad-observer.lsp")
echo.
echo 3. In AutoCAD, type: CAD-OBSERVER-START
echo.
echo 4. Run click_capture.py for screenshot capture:
echo    python click_capture.py --project "Your Project"
echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.

pause
