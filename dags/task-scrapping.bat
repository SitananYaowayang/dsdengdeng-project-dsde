@echo off
chcp 65001 > nul

REM =====================================================
REM ตั้งให้ทำงานจากโฟลเดอร์ที่ไฟล์ .bat นี้อยู่ (คือ dags)
REM =====================================================
set "DAGS_DIR=%~dp0"
pushd "%DAGS_DIR%"

echo ==========================================
echo Starting Data Pipeline (Scraping)...
echo Working directory: %CD%
echo ==========================================
echo.

REM ถ้าอยากให้ bat activate env เอง ให้ uncomment บรรทัดนี้
REM call "%USERPROFILE%\anaconda3\Scripts\activate.bat" dsde

REM 1) รันไฟล์ Web Scraping ของ Traffy Fondue
echo [Step 1/2] Scraping Traffy Fondue Data...
python "scrapping\traffy-fondue-get-data.py"

if %errorlevel% neq 0 (
    echo [ERROR] Error occurred in Scraping Traffy step!
    pause
    popd
    exit /b %errorlevel%
)

echo.

@REM REM 2) รันไฟล์ Web Scraping ของ DDProperty
@REM echo [Step 2/2] Scraping DDProperty Data...
@REM python "scrapping\main.py"

@REM if %errorlevel% neq 0 (
@REM     echo [ERROR] Error occurred in Scraping DDProperty step!
@REM     pause
@REM     popd
@REM     exit /b %errorlevel%
@REM )

@REM echo.
echo ------------------------------------------
echo ✅ All Scraping Tasks Completed Successfully!
echo ------------------------------------------
pause

REM กลับไปโฟลเดอร์เดิม
popd
