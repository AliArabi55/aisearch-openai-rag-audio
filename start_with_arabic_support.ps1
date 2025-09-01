# إعداد PowerShell لدعم النصوص العربية بشكل أفضل
# تشغيل هذا الملف قبل تشغيل التطبيق

Write-Host "🔧 إعداد PowerShell لدعم اللغة العربية..." -ForegroundColor Green

# تعيين UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# تعيين code page إلى UTF-8
chcp 65001 | Out-Null

# تعيين culture إلى العربية
$culture = [System.Globalization.CultureInfo]::CreateSpecificCulture("ar-EG")
[System.Threading.Thread]::CurrentThread.CurrentCulture = $culture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = $culture

Write-Host "✅ تم إعداد الترميز بنجاح" -ForegroundColor Green
Write-Host "📝 الآن يمكن عرض النصوص العربية بشكل صحيح" -ForegroundColor Yellow
Write-Host "🚀 جاري تشغيل التطبيق..." -ForegroundColor Cyan

# تشغيل التطبيق
Set-Location "C:\Users\aliar\OneDrive\Documents\GitHub\aisearch-openai-rag-audio"
& .\.venv\Scripts\python.exe app\backend\app.py
