@echo off
chcp 65001 > nul

REM =====================================================
REM ตั้งให้ทำงานจากโฟลเดอร์ที่ไฟล์ .bat นี้อยู่ (คือ dags)
REM =====================================================
set "DAGS_DIR=%~dp0"
pushd "%DAGS_DIR%"

echo ==========================================
echo Starting Data Cleaning...
echo Working directory: %CD%
echo ==========================================
echo.

REM ถ้าอยากให้ bat activate env เอง ให้ uncomment บรรทัดนี้
REM call "%USERPROFILE%\anaconda3\Scripts\activate.bat" dsde

REM 1) รัน Notebook ทำความสะอาด Traffy
echo [Step 1/2] Cleaning Traffy Data (running notebook)...
jupyter nbconvert --to notebook --execute --inplace "clean\clean-traffy-fondue.ipynb"

if %errorlevel% neq 0 (
    echo [ERROR] Cleaning Traffy step failed!
    pause
    popd
    exit /b %errorlevel%
)

echo.

@REM REM 2) รันสคริปต์ทำความสะอาด DDProperty
@REM echo [Step 2/2] Cleaning DDProperty Data...
@REM python "clean\clean-ddproperty.py"

@REM if %errorlevel% neq 0 (
@REM     echo [ERROR] Cleaning DDProperty step failed!
@REM     pause
@REM     popd
@REM     exit /b %errorlevel%
@REM )

@REM echo.
@REM echo ==========================================
@REM echo ✅ All Cleaning Tasks Completed Successfully!
@REM echo ==========================================
@REM pause

REM กลับไปโฟลเดอร์เดิม (ก่อน pushd)
popd
