@echo off
chcp 65001 > nul
echo ==========================================
echo Starting Data Pipeline...
echo ==========================================

:: 1. รันไฟล์ Web Scraping (Python Script)
echo [Step 1/2] Scraping Traffy Fondue Data...
python "C:\Users\sasit\CU\2-1\dsde\project\dsdengdeng-project-dsde\dags\scrapping\traffy-fondue-get-data.py"

:: ตรวจสอบว่า Scraping สำเร็จไหม (ถ้า error ให้หยุด)
if %errorlevel% neq 0 (
    echo Error occurred in Scraping step!
    pause
    exit /b %errorlevel%
)

echo.
echo ------------------------------------------
echo.

:: 2. รันไฟล์ Data Cleaning (Jupyter Notebook)
:: คำสั่งนี้จะรันทุก Cell ใน Notebook และเซฟผลลัพธ์ทับลงไปในไฟล์เดิม
echo [Step 2/2] Cleaning Data (Running Notebook)...
jupyter nbconvert --to notebook --execute --inplace "C:\Users\sasit\CU\2-1\dsde\project\dsdengdeng-project-dsde\dags\clean\clean-traffy-fondue.ipynb"

:: ตรวจสอบว่า Cleaning สำเร็จไหม
if %errorlevel% neq 0 (
    echo Error occurred in Cleaning step!
    pause
    exit /b %errorlevel%
)

echo.
echo ==========================================
echo ✅ All Tasks Completed Successfully!
echo ==========================================
pause