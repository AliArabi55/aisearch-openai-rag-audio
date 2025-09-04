@echo off
chcp 65001 > nul
echo 🚀 تشغيل مطعم سيركلز مع دعم اللغة العربية
echo ========================================
echo.
echo 🔧 جاري إعداد الترميز...
echo ✅ تم تعيين UTF-8 بنجاح
echo.
echo 📱 سيتم فتح التطبيق على: http://localhost:8765
echo.
echo 🎵 تسلسل الأصوات:
echo    1. Ran.mp3 (رسالة ترحيب)
echo    2. between.wav (فاصل موسيقي) 
echo    3. Nancy.wav (بداية المحادثة)
echo.
echo 🗣️ بعد الأصوات قل: "عايز أطلب بيتزا فراخ كبيرة"
echo.
echo 🛑 للإيقاف اضغط Ctrl+C
echo.
cd /d "C:\Users\aliar\OneDrive\Documents\GitHub\aisearch-openai-rag-audio"
.\.venv\Scripts\python.exe app\backend\app.py
