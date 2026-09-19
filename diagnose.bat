@echo off
chcp 65001 >nul
title Windows E-Imza ve Akilli Kart Surucu Teshis Araci
echo ====================================================================
echo  E-Imza ve Akilli Kart Donanim/Surucu Teshisi Calistiriliyor...
echo ====================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Diagnose-SmartCard.ps1"

echo.
pause
