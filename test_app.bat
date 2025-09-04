@echo off
echo Testing localhost:8765...
curl -s http://localhost:8765 > nul
if %errorlevel% == 0 (
    echo ✅ التطبيق يعمل
    echo.
    echo Testing search endpoint...
    curl -X POST http://localhost:8765/search -H "Content-Type: application/json" -d "{\"query\":\"أريد بيتزا تونة وسط\"}"
    echo.
    echo.
    echo Testing with another query...
    curl -X POST http://localhost:8765/search -H "Content-Type: application/json" -d "{\"query\":\"عايز كباب دجاج\"}"
) else (
    echo ❌ التطبيق لا يعمل
)
