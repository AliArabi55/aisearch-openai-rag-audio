#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار محدد لـ Real-time API
Test Real-time API specifically
"""

import asyncio
import json
import os
import sys
import websockets
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

class RealtimeAPITester:
    def __init__(self):
        self.base_url = "localhost:8765"
        self.websocket_url = f"ws://{self.base_url}/realtime"
        
    async def test_websocket_connection(self):
        """اختبار اتصال WebSocket"""
        print_arabic("🔌 اختبار اتصال WebSocket...")
        
        try:
            # محاولة الاتصال بـ WebSocket
            async with websockets.connect(self.websocket_url) as websocket:
                print_arabic("✅ تم الاتصال بـ WebSocket بنجاح!")
                
                # إرسال رسالة اختبار
                test_message = {
                    "type": "response.create",
                    "response": {
                        "modalities": ["text"],
                        "instructions": "أنت موظف طلبات في مطعم سيركلز"
                    }
                }
                
                await websocket.send(json.dumps(test_message))
                print_arabic("📤 تم إرسال رسالة اختبار")
                
                # انتظار الرد
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    print_arabic("📥 تم استلام رد من السيرفر:")
                    print_arabic(f"   {response[:200]}...")
                    
                    return True
                    
                except asyncio.TimeoutError:
                    print_arabic("⏰ انتهت مهلة انتظار الرد")
                    return False
                    
        except websockets.exceptions.ConnectionRefused:
            print_arabic("❌ فشل الاتصال: السيرفر رفض الاتصال")
            return False
        except websockets.exceptions.InvalidURI:
            print_arabic("❌ رابط WebSocket غير صحيح")
            return False
        except Exception as e:
            print_arabic(f"❌ خطأ في اتصال WebSocket: {str(e)}")
            return False
    
    async def test_basic_http(self):
        """اختبار HTTP الأساسي"""
        import aiohttp
        
        print_arabic("🌐 اختبار HTTP الأساسي...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # اختبار الصفحة الرئيسية
                async with session.get(f"http://{self.base_url}") as response:
                    if response.status == 200:
                        print_arabic("✅ الصفحة الرئيسية تعمل")
                        return True
                    else:
                        print_arabic(f"❌ الصفحة الرئيسية - كود الخطأ: {response.status}")
                        return False
        except Exception as e:
            print_arabic(f"❌ خطأ في HTTP: {str(e)}")
            return False
    
    def check_env_file(self):
        """فحص ملف .env"""
        print_arabic("📋 فحص ملف .env...")
        
        env_path = Path("app/backend/.env")
        if not env_path.exists():
            print_arabic("❌ ملف .env غير موجود")
            return False
        
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY", 
            "AZURE_OPENAI_REALTIME_DEPLOYMENT",
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_SEARCH_API_KEY",
            "AZURE_SEARCH_INDEX"
        ]
        
        missing_vars = []
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for var in required_vars:
                if var not in content or f"{var}=" not in content:
                    missing_vars.append(var)
        except Exception as e:
            print_arabic(f"❌ خطأ في قراءة ملف .env: {str(e)}")
            return False
        
        if missing_vars:
            print_arabic("❌ متغيرات مفقودة في ملف .env:")
            for var in missing_vars:
                print_arabic(f"   - {var}")
            return False
        else:
            print_arabic("✅ جميع المتغيرات المطلوبة موجودة في ملف .env")
            return True
    
    async def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل"""
        print_arabic("🚀 اختبار Real-time API الشامل")
        print_arabic("=" * 50)
        
        # 1. فحص ملف .env
        env_ok = self.check_env_file()
        
        # 2. اختبار HTTP الأساسي
        http_ok = await self.test_basic_http()
        
        # 3. اختبار WebSocket
        websocket_ok = False
        if http_ok:
            websocket_ok = await self.test_websocket_connection()
        else:
            print_arabic("⏭️  تخطي اختبار WebSocket - HTTP لا يعمل")
        
        # النتائج
        print_arabic("\n📊 نتائج الاختبار:")
        print_arabic("=" * 50)
        print_arabic(f"📋 ملف .env: {'✅ صحيح' if env_ok else '❌ مشكلة'}")
        print_arabic(f"🌐 HTTP: {'✅ يعمل' if http_ok else '❌ معطل'}")
        print_arabic(f"🔌 WebSocket (Real-time): {'✅ يعمل' if websocket_ok else '❌ معطل'}")
        
        # التوصيات
        print_arabic("\n💡 التوصيات:")
        if not env_ok:
            print_arabic("🔧 تحقق من ملف .env وتأكد من وجود جميع المتغيرات")
        if not http_ok:
            print_arabic("🔧 تأكد من تشغيل التطبيق على localhost:8765")
        if http_ok and not websocket_ok:
            print_arabic("🔧 مشكلة في Real-time API - تحقق من:")
            print_arabic("   - AZURE_OPENAI_REALTIME_DEPLOYMENT")
            print_arabic("   - AZURE_OPENAI_API_KEY")
            print_arabic("   - إعدادات Azure OpenAI")
        
        if env_ok and http_ok and websocket_ok:
            print_arabic("🎉 جميع الاختبارات نجحت! Real-time API يعمل بشكل مثالي")
        
        return env_ok and http_ok and websocket_ok

async def main():
    """الدالة الرئيسية"""
    print_arabic("🎯 اختبار Real-time API")
    
    tester = RealtimeAPITester()
    
    try:
        success = await tester.run_comprehensive_test()
        
        if success:
            print_arabic("\n🎉 Real-time API يعمل بنجاح!")
        else:
            print_arabic("\n⚠️  هناك مشاكل في Real-time API تحتاج لحل")
        
        return success
        
    except KeyboardInterrupt:
        print_arabic("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print_arabic(f"\n❌ خطأ غير متوقع: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(main())
