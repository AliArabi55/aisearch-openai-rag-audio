#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار Real-time API - فحص أساسي
Basic Real-time API Test
"""

import asyncio
import aiohttp
import json
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

async def test_realtime_basic():
    """اختبار Real-time API الأساسي"""
    print_arabic("🔍 اختبار Real-time API...")
    
    # فحص ملف .env
    print_arabic("\n📋 فحص ملف .env...")
    env_path = Path("app/backend/.env")
    
    if not env_path.exists():
        print_arabic("❌ ملف .env غير موجود في app/backend/.env")
        return False
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
            
        print_arabic("✅ ملف .env موجود")
        
        # فحص المتغيرات المطلوبة
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY", 
            "AZURE_OPENAI_REALTIME_DEPLOYMENT"
        ]
        
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)
            else:
                # استخراج القيمة
                lines = env_content.split('\n')
                for line in lines:
                    if line.startswith(f"{var}="):
                        value = line.split('=', 1)[1].strip()
                        if not value or value == '""' or value == "''":
                            missing_vars.append(f"{var} (قيمة فارغة)")
                        else:
                            print_arabic(f"✅ {var}: {value[:20]}...")
        
        if missing_vars:
            print_arabic("❌ متغيرات مفقودة أو فارغة:")
            for var in missing_vars:
                print_arabic(f"   - {var}")
            return False
            
    except Exception as e:
        print_arabic(f"❌ خطأ في قراءة ملف .env: {str(e)}")
        return False
    
    # اختبار HTTP
    print_arabic("\n🌐 اختبار اتصال HTTP...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8765") as response:
                if response.status == 200:
                    print_arabic("✅ التطبيق يعمل على localhost:8765")
                else:
                    print_arabic(f"❌ التطبيق - كود الخطأ: {response.status}")
                    return False
    except Exception as e:
        print_arabic(f"❌ خطأ في الاتصال: {str(e)}")
        print_arabic("💡 تأكد من تشغيل التطبيق أولاً")
        return False
    
    # اختبار Real-time endpoint
    print_arabic("\n⚡ اختبار Real-time endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            # اختبار الـ endpoint مع WebSocket headers
            headers = {
                'Upgrade': 'websocket',
                'Connection': 'Upgrade',
                'Sec-WebSocket-Key': 'test',
                'Sec-WebSocket-Version': '13'
            }
            
            async with session.get("http://localhost:8765/realtime", headers=headers) as response:
                if response.status == 101:  # Switching Protocols
                    print_arabic("✅ Real-time endpoint يدعم WebSocket")
                    return True
                elif response.status == 426:  # Upgrade Required
                    print_arabic("✅ Real-time endpoint متاح (يطلب WebSocket)")
                    return True
                elif response.status == 400:
                    print_arabic("⚠️  Real-time endpoint متاح لكن يحتاج WebSocket صحيح")
                    return True
                else:
                    print_arabic(f"❌ Real-time endpoint - كود الخطأ: {response.status}")
                    return False
                    
    except Exception as e:
        print_arabic(f"❌ خطأ في Real-time endpoint: {str(e)}")
        return False

async def main():
    """الدالة الرئيسية"""
    print_arabic("🎯 اختبار Real-time API الأساسي")
    print_arabic("=" * 50)
    
    try:
        success = await test_realtime_basic()
        
        print_arabic("\n📊 النتيجة:")
        if success:
            print_arabic("✅ Real-time API جاهز للعمل!")
            print_arabic("💡 جرب فتح localhost:8765 في المتصفح للاختبار التفاعلي")
        else:
            print_arabic("❌ هناك مشاكل في Real-time API")
            print_arabic("💡 راجع الرسائل أعلاه لمعرفة المشاكل")
            
    except Exception as e:
        print_arabic(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
