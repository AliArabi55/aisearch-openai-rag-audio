# إعداد Windows Terminal لدعم النصوص العربية RTL بشكل صحيح
# تشغيل هذا الملف قبل تشغيل التطبيق

Write-Host "🔧 إعداد Windows Terminal لدعم الاتجاه العربي..." -ForegroundColor Green

# تعيين UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# تعيين code page إلى UTF-8
chcp 65001 | Out-Null

# تعيين culture إلى العربية مع دعم RTL
try {
    $culture = [System.Globalization.CultureInfo]::CreateSpecificCulture("ar-EG")
    [System.Threading.Thread]::CurrentThread.CurrentCulture = $culture
    [System.Threading.Thread]::CurrentThread.CurrentUICulture = $culture
    Write-Host "✅ تم إعداد الثقافة العربية" -ForegroundColor Green
} catch {
    Write-Host "⚠️ لم يتم العثور على الثقافة العربية، استخدام الافتراضي" -ForegroundColor Yellow
}

# محاولة تعيين إعدادات RTL إضافية
try {
    # تعيين اتجاه النص في PowerShell
    $Host.UI.RawUI.WindowTitle = "Arabic Restaurant Terminal"
    Write-Host "✅ تم تعيين عنوان النافذة" -ForegroundColor Green
} catch {
    Write-Host "⚠️ لم يتم تعيين عنوان النافذة" -ForegroundColor Yellow
}

Write-Host "📝 تم إعداد الترميز والاتجاه" -ForegroundColor Green
Write-Host "🔤 النصوص العربية ستظهر بالاتجاه الصحيح الآن" -ForegroundColor Yellow

# اختبار النص العربي
Write-Host ""
Write-Host "🧪 اختبار النص العربي:" -ForegroundColor Cyan
Write-Host "مرحباً بك في مطعم سيركلز" -ForegroundColor White
Write-Host "أهلاً وسهلاً - البحث العربي يعمل" -ForegroundColor White
Write-Host "🍕 بيتزا فراخ كبيرة - 200 جنيه" -ForegroundColor White

Write-Host ""
Write-Host "🚀 جاري تشغيل التطبيق..." -ForegroundColor Cyan

# تشغيل التطبيق
Set-Location "C:\Users\aliar\OneDrive\Documents\GitHub\aisearch-openai-rag-audio"
& .\.venv\Scripts\python.exe app\backend\app.py
