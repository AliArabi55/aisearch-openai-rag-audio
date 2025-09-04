#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تفاعلي لـ Real-time API
Interactive Real-time API Test
"""

import asyncio
import aiohttp
import json
import sys

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

async def test_realtime_manual():
    """اختبار Real-time يدوي"""
    print_arabic("🎮 اختبار Real-time API التفاعلي")
    print_arabic("=" * 50)
    
    # التحقق من التطبيق
    print_arabic("🔍 التحقق من التطبيق...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8765") as response:
                if response.status != 200:
                    print_arabic(f"❌ التطبيق لا يعمل - كود الخطأ: {response.status}")
                    return
                print_arabic("✅ التطبيق يعمل")
    except Exception as e:
        print_arabic(f"❌ خطأ في الاتصال: {str(e)}")
        print_arabic("💡 تأكد من تشغيل التطبيق أولاً:")
        print_arabic("   cd app")
        print_arabic("   .\\.venv\\Scripts\\python.exe backend\\app.py")
        return
    
    print_arabic("\n🌐 افتح المتصفح على: http://localhost:8765")
    print_arabic("🎤 للاختبار الكامل:")
    print_arabic("   1. اضغط على زر الميكروفون")
    print_arabic("   2. قل: 'مساء الخير'")
    print_arabic("   3. انتظر الرد")
    print_arabic("   4. جرب طلب: 'أريد بيتزا تونة وسط'")
    
    print_arabic("\n🔧 خطوات استكشاف الأخطاء:")
    print_arabic("   1. تأكد من السماح للمتصفح بالوصول للميكروفون")
    print_arabic("   2. تحقق من وجود اتصال بالإنترنت")
    print_arabic("   3. تأكد من صحة مفاتيح Azure OpenAI API")
    
    print_arabic("\n📊 حالة المكونات:")
    
    # اختبار الصوت
    print_arabic("🎵 ملفات الصوت:")
    audio_files = ["Ran.mp3", "between.wav", "Nancy.wav"]
    for audio_file in audio_files:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:8765/audio/{audio_file}") as response:
                    if response.status == 200:
                        print_arabic(f"   ✅ {audio_file}")
                    else:
                        print_arabic(f"   ❌ {audio_file}")
        except:
            print_arabic(f"   ❌ {audio_file}")
    
    # اختبار Real-time endpoint
    print_arabic("⚡ Real-time:")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8765/realtime") as response:
                if response.status in [400, 426]:  # هذا طبيعي للـ WebSocket
                    print_arabic("   ✅ Real-time endpoint متاح")
                else:
                    print_arabic(f"   ⚠️  Real-time endpoint - كود: {response.status}")
    except:
        print_arabic("   ❌ Real-time endpoint")
    
    print_arabic("\n🎯 الخطوة التالية:")
    print_arabic("   افتح http://localhost:8765 في المتصفح واختبر الميكروفون!")

if __name__ == "__main__":
    asyncio.run(test_realtime_manual())
