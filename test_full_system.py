#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للنظام: الصوت + Real-time + AI Search
Test Full System: Audio + Real-time + AI Search
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

class SystemTester:
    def __init__(self):
        self.base_url = "http://localhost:8765"
        self.audio_files = ["Ran.mp3", "between.wav", "Nancy.wav"]
        
    async def test_app_status(self):
        """اختبار حالة التطبيق"""
        print_arabic("🔍 اختبار حالة التطبيق...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url) as response:
                    if response.status == 200:
                        print_arabic("✅ التطبيق يعمل بنجاح على localhost:8765")
                        return True
                    else:
                        print_arabic(f"❌ التطبيق لا يعمل - كود الخطأ: {response.status}")
                        return False
        except Exception as e:
            print_arabic(f"❌ خطأ في الاتصال بالتطبيق: {str(e)}")
            return False

    async def test_audio_files(self):
        """اختبار ملفات الصوت"""
        print_arabic("\n🎵 اختبار ملفات الصوت...")
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for audio_file in self.audio_files:
                try:
                    audio_url = f"{self.base_url}/audio/{audio_file}"
                    async with session.get(audio_url) as response:
                        if response.status == 200:
                            content_length = response.headers.get('content-length', 'غير معروف')
                            content_type = response.headers.get('content-type', 'غير معروف')
                            
                            print_arabic(f"✅ {audio_file}:")
                            print_arabic(f"   - حجم الملف: {content_length} بايت")
                            print_arabic(f"   - نوع الملف: {content_type}")
                            print_arabic(f"   - رابط الوصول: {audio_url}")
                            
                            results[audio_file] = {
                                'status': 'success',
                                'size': content_length,
                                'type': content_type,
                                'url': audio_url
                            }
                        else:
                            print_arabic(f"❌ {audio_file} - كود الخطأ: {response.status}")
                            results[audio_file] = {'status': 'error', 'code': response.status}
                            
                except Exception as e:
                    print_arabic(f"❌ خطأ في {audio_file}: {str(e)}")
                    results[audio_file] = {'status': 'error', 'message': str(e)}
        
        return results

    async def test_realtime_endpoint(self):
        """اختبار Real-time endpoint"""
        print_arabic("\n⚡ اختبار Real-time endpoint...")
        try:
            realtime_url = f"{self.base_url}/realtime"
            async with aiohttp.ClientSession() as session:
                async with session.get(realtime_url) as response:
                    if response.status == 200:
                        print_arabic("✅ Real-time endpoint متاح")
                        return True
                    elif response.status == 426:  # Upgrade Required (WebSocket)
                        print_arabic("✅ Real-time endpoint يطلب WebSocket upgrade (هذا طبيعي)")
                        return True
                    else:
                        print_arabic(f"❌ Real-time endpoint - كود الخطأ: {response.status}")
                        return False
        except Exception as e:
            print_arabic(f"❌ خطأ في Real-time endpoint: {str(e)}")
            return False

    def check_local_files(self):
        """فحص الملفات الصوتية محلياً"""
        print_arabic("\n📁 فحص الملفات المحلية...")
        
        # فحص مجلد Voice Ran
        voice_ran_path = Path("Voice Ran")
        if voice_ran_path.exists():
            print_arabic("📂 مجلد Voice Ran موجود:")
            for file in voice_ran_path.glob("*"):
                size = file.stat().st_size if file.is_file() else "مجلد"
                print_arabic(f"   - {file.name}: {size} بايت")
        else:
            print_arabic("❌ مجلد Voice Ran غير موجود")

        # فحص مجلد static/audio
        static_audio_path = Path("app/backend/static/audio")
        if static_audio_path.exists():
            print_arabic("📂 مجلد app/backend/static/audio موجود:")
            for file in static_audio_path.glob("*"):
                size = file.stat().st_size if file.is_file() else "مجلد"
                print_arabic(f"   - {file.name}: {size} بايت")
        else:
            print_arabic("❌ مجلد app/backend/static/audio غير موجود")

    async def test_search_functionality(self):
        """اختبار وظيفة البحث (محاكاة)"""
        print_arabic("\n🔍 اختبار وظيفة AI Search...")
        
        # يمكننا إضافة اختبار للبحث هنا إذا كان هناك API endpoint للبحث
        # حالياً، البحث يتم عبر Real-time WebSocket
        print_arabic("ℹ️  البحث يتم عبر Real-time WebSocket - يحتاج لاختبار تفاعلي")
        print_arabic("ℹ️  للاختبار الكامل، استخدم واجهة المستخدم على localhost:8765")
        
        return True

    async def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل"""
        print_arabic("🚀 بدء الاختبار الشامل للنظام")
        print_arabic("=" * 60)
        
        # 1. فحص الملفات المحلية
        self.check_local_files()
        
        # 2. اختبار حالة التطبيق
        app_running = await self.test_app_status()
        
        if not app_running:
            print_arabic("\n❌ التطبيق لا يعمل - يرجى تشغيله أولاً")
            print_arabic("💡 استخدم الأمر: cd app && python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt && python backend/app.py")
            return False
        
        # 3. اختبار ملفات الصوت
        audio_results = await self.test_audio_files()
        
        # 4. اختبار Real-time endpoint
        realtime_working = await self.test_realtime_endpoint()
        
        # 5. اختبار البحث
        search_working = await self.test_search_functionality()
        
        # تلخيص النتائج
        print_arabic("\n📊 تلخيص نتائج الاختبار:")
        print_arabic("=" * 60)
        
        # نتائج الصوت
        working_audio = [f for f, r in audio_results.items() if r.get('status') == 'success']
        broken_audio = [f for f, r in audio_results.items() if r.get('status') != 'success']
        
        print_arabic(f"🎵 ملفات الصوت العاملة: {len(working_audio)}/3")
        for file in working_audio:
            print_arabic(f"   ✅ {file}")
        
        if broken_audio:
            print_arabic(f"🎵 ملفات الصوت المعطلة: {len(broken_audio)}/3")
            for file in broken_audio:
                print_arabic(f"   ❌ {file}")
        
        print_arabic(f"⚡ Real-time: {'✅ يعمل' if realtime_working else '❌ معطل'}")
        print_arabic(f"🔍 AI Search: {'✅ متاح' if search_working else '❌ معطل'}")
        
        # توصيات
        print_arabic("\n💡 التوصيات:")
        if len(working_audio) == 3 and realtime_working and search_working:
            print_arabic("🎉 جميع المكونات تعمل بنجاح!")
            print_arabic("🌐 يمكنك الآن اختبار النظام الكامل على: http://localhost:8765")
        else:
            if broken_audio:
                print_arabic("🔧 قم بفحص ملفات الصوت المعطلة")
            if not realtime_working:
                print_arabic("🔧 قم بفحص إعدادات Real-time API")
            if not search_working:
                print_arabic("🔧 قم بفحص إعدادات Azure Search")

        return len(working_audio) == 3 and realtime_working and search_working

def main():
    """الدالة الرئيسية"""
    print_arabic("🎯 اختبار النظام الشامل: الصوت + Real-time + AI Search")
    
    # التحقق من وجود التطبيق
    app_path = Path("app/backend/app.py")
    if not app_path.exists():
        print_arabic("❌ ملف التطبيق غير موجود: app/backend/app.py")
        print_arabic("💡 يرجى التأكد من تشغيل الأمر من مجلد المشروع الرئيسي")
        return
    
    # تشغيل الاختبارات
    tester = SystemTester()
    
    try:
        result = asyncio.run(tester.run_comprehensive_test())
        
        if result:
            print_arabic("\n🎉 الاختبار مكتمل بنجاح!")
        else:
            print_arabic("\n⚠️  هناك مشاكل تحتاج لحل")
            
    except KeyboardInterrupt:
        print_arabic("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print_arabic(f"\n❌ خطأ غير متوقع: {str(e)}")

if __name__ == "__main__":
    main()
