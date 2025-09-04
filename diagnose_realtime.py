#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص شامل لإعدادات Real-time API
Comprehensive Real-time API Configuration Check
"""

import os
import sys
from pathlib import Path

# إعداد الترميز للنصوص العربية
import locale
locale.setlocale(locale.LC_ALL, '')

if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def print_arabic(text):
    """طباعة النصوص العربية بشكل صحيح"""
    try:
        print(text.encode('utf-8').decode('utf-8'))
    except:
        print(text)

def check_realtime_config():
    """فحص إعدادات Real-time"""
    print_arabic("🔧 فحص إعدادات Real-time API")
    print_arabic("=" * 50)
    
    # فحص ملف .env
    env_path = Path("app/backend/.env")
    
    if not env_path.exists():
        print_arabic("❌ ملف .env غير موجود")
        return False
    
    # قراءة الملف
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print_arabic(f"❌ خطأ في قراءة .env: {str(e)}")
        return False
    
    print_arabic("📋 إعدادات Real-time الحالية:")
    
    # استخراج المتغيرات
    config = {}
    for line in content.split('\n'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()
    
    # فحص الإعدادات المطلوبة
    required_configs = {
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI Endpoint',
        'AZURE_OPENAI_API_KEY': 'Azure OpenAI API Key',
        'AZURE_OPENAI_REALTIME_DEPLOYMENT': 'Real-time Deployment',
        'AZURE_OPENAI_REALTIME_VOICE_CHOICE': 'Voice Choice (اختياري)'
    }
    
    all_good = True
    
    for key, description in required_configs.items():
        if key in config:
            value = config[key]
            if value and value not in ['""', "''"]:
                if 'KEY' in key:
                    print_arabic(f"✅ {description}: {value[:10]}...{value[-10:]}")
                elif 'ENDPOINT' in key:
                    print_arabic(f"✅ {description}: {value}")
                else:
                    print_arabic(f"✅ {description}: {value}")
            else:
                print_arabic(f"❌ {description}: قيمة فارغة")
                all_good = False
        else:
            if key != 'AZURE_OPENAI_REALTIME_VOICE_CHOICE':  # اختياري
                print_arabic(f"❌ {description}: غير موجود")
                all_good = False
            else:
                print_arabic(f"⚠️  {description}: غير محدد (سيستخدم 'alloy')")
    
    # فحص deployment name
    if 'AZURE_OPENAI_REALTIME_DEPLOYMENT' in config:
        deployment = config['AZURE_OPENAI_REALTIME_DEPLOYMENT']
        if 'realtime' not in deployment.lower():
            print_arabic(f"⚠️  اسم Deployment قد لا يكون صحيح: {deployment}")
            print_arabic("💡 تأكد من أن اسم deployment يحتوي على 'realtime'")
    
    print_arabic(f"\n📊 حالة الإعدادات: {'✅ جميع الإعدادات صحيحة' if all_good else '❌ هناك مشاكل'}")
    
    # التوصيات
    if not all_good:
        print_arabic("\n💡 لحل المشاكل:")
        print_arabic("1. تأكد من إنشاء Real-time deployment في Azure OpenAI Studio")
        print_arabic("2. استخدم model: gpt-4o-realtime-preview")
        print_arabic("3. انسخ اسم deployment الصحيح")
        print_arabic("4. تأكد من صحة API key")
    
    return all_good

def check_app_structure():
    """فحص هيكل التطبيق"""
    print_arabic("\n📁 فحص هيكل التطبيق:")
    
    required_files = [
        "app/backend/app.py",
        "app/backend/static/index.html",
        "app/backend/static/audio/Ran.mp3",
        "app/backend/static/audio/between.wav", 
        "app/backend/static/audio/Nancy.wav"
    ]
    
    all_files_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print_arabic(f"✅ {file_path}")
        else:
            print_arabic(f"❌ {file_path}")
            all_files_exist = False
    
    return all_files_exist

def main():
    """الدالة الرئيسية"""
    print_arabic("🎯 فحص شامل لـ Real-time API")
    
    # فحص الإعدادات
    config_ok = check_realtime_config()
    
    # فحص الملفات
    files_ok = check_app_structure()
    
    print_arabic("\n🎯 الخلاصة:")
    print_arabic("=" * 50)
    
    if config_ok and files_ok:
        print_arabic("🎉 جميع الإعدادات والملفات صحيحة!")
        print_arabic("💡 إذا كان Real-time لا يعمل، جرب:")
        print_arabic("   1. إعادة تشغيل التطبيق")
        print_arabic("   2. تحديث المتصفح")
        print_arabic("   3. التحقق من إعدادات الميكروفون")
        print_arabic("   4. فحص console في المتصفح للأخطاء")
    else:
        print_arabic("⚠️  هناك مشاكل تحتاج لحل:")
        if not config_ok:
            print_arabic("   - مشاكل في إعدادات .env")
        if not files_ok:
            print_arabic("   - ملفات مفقودة")
    
    print_arabic(f"\n🌐 التطبيق متاح على: http://localhost:8765")

if __name__ == "__main__":
    main()
