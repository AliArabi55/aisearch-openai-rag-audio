"""
🔧 اختبار اتصال Azure OpenAI Realtime API
==========================================
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'app', 'backend', '.env'))

async def test_realtime_api():
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    deployment = os.environ.get("AZURE_OPENAI_REALTIME_DEPLOYMENT") 
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    
    print("🔍 اختبار Azure OpenAI Realtime API:")
    print(f"🌐 الخادم: {endpoint}")
    print(f"🚀 النموذج: {deployment}")
    print(f"🔑 المفتاح: {'✅ موجود' if api_key else '❌ مفقود'}")
    
    # تكوين الطلب
    url = f"{endpoint}/openai/realtime"
    params = {
        "api-version": "2024-10-01-preview",
        "deployment": deployment
    }
    headers = {
        "api-key": api_key
    }
    
    print(f"\n🔗 رابط الاختبار: {url}")
    print(f"📊 المعاملات: {params}")
    
    try:
        # محاولة اتصال WebSocket
        async with aiohttp.ClientSession() as session:
            print("\n📡 محاولة الاتصال...")
            async with session.ws_connect(
                url,
                headers=headers,
                params=params
            ) as ws:
                print("✅ نجح الاتصال!")
                print("🎯 Real-time API يعمل بشكل صحيح")
                
                # إرسال رسالة اختبار بسيطة
                test_message = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text"],
                        "instructions": "أنت مساعد ذكي"
                    }
                }
                
                await ws.send_str(str(test_message))
                
                # انتظار الرد
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        print(f"📨 رد من الخادم: {msg.data[:100]}...")
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"❌ خطأ: {msg.data}")
                        break
                        
    except aiohttp.ClientResponseError as e:
        print(f"❌ خطأ HTTP: {e.status} - {e.message}")
        if e.status == 401:
            print("🔑 المشكلة: مفتاح API غير صحيح أو منتهي الصلاحية")
        elif e.status == 404:
            print("🚀 المشكلة: اسم النموذج غير صحيح")
        elif e.status == 403:
            print("🔒 المشكلة: لا توجد صلاحية للوصول")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

if __name__ == "__main__":
    asyncio.run(test_realtime_api())
