#!/usr/bin/env pwsh

Write-Host "🚀 بدء تطبيق RAG الصوتي مع Azure AI Search..." -ForegroundColor Green

# تفعيل البيئة الافتراضية
Write-Host "📦 تفعيل البيئة الافتراضية..." -ForegroundColor Yellow
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"

# الانتقال إلى مجلد backend
Set-Location "$PSScriptRoot\backend"

# تحديد المنفذ
$env:PORT = "8765"

Write-Host "🌐 تشغيل التطبيق على المنفذ 8765..." -ForegroundColor Green
Write-Host "🔗 الرابط: http://localhost:8765" -ForegroundColor Cyan

# تشغيل التطبيق
& python app.py
