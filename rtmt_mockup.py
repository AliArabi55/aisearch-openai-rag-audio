"""
🔧 حل مؤقت: Real-time محاكي للاختبار
=====================================

هذا محاكي مؤقت لاختبار وظائف النظام بدون Real-time API
حتى يتم حل مشكلة مفتاح API
"""

from aiohttp import web
import json
import asyncio
import logging

logger = logging.getLogger("voicerag")

class RTMTMockup:
    """محاكي مؤقت لـ Real-time API"""
    
    def __init__(self):
        self.tools = {}
        self.system_message = ""
    
    def attach_to_app(self, app: web.Application):
        """ربط المحاكي بالتطبيق"""
        app.router.add_get("/rtmt", self._websocket_handler)
        
        # إضافة صفحة اختبار بسيطة
        app.router.add_get("/test", self._test_handler)
    
    async def _test_handler(self, request):
        """صفحة اختبار بسيطة"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Real-time محاكي</title>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🔧 Real-time محاكي مؤقت</h1>
            <p>هذا محاكي مؤقت لاختبار النظام</p>
            <div style="background: #f0f0f0; padding: 20px; margin: 20px; border-radius: 10px;">
                <h3>المشكلة:</h3>
                <p>مفتاح Azure OpenAI Real-time API غير صحيح أو منتهي الصلاحية</p>
                <h3>الحل:</h3>
                <p>تجديد المفتاح من Azure Portal أو التحقق من النموذج المنشور</p>
            </div>
            <button onclick="testSearch()" style="padding: 10px 20px; font-size: 16px;">
                اختبار البحث
            </button>
            <div id="result" style="margin-top: 20px;"></div>
            
            <script>
                async function testSearch() {
                    const result = document.getElementById('result');
                    result.innerHTML = '🔍 جاري البحث...';
                    
                    try {
                        const response = await fetch('/api/test-search', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ query: 'بيتزا تونة وسط' })
                        });
                        
                        const data = await response.json();
                        result.innerHTML = `
                            <div style="background: #e8f5e8; padding: 15px; border-radius: 5px;">
                                <h4>✅ نتيجة البحث:</h4>
                                <p>${data.result}</p>
                            </div>
                        `;
                    } catch (error) {
                        result.innerHTML = `
                            <div style="background: #f5e8e8; padding: 15px; border-radius: 5px;">
                                <h4>❌ خطأ:</h4>
                                <p>${error.message}</p>
                            </div>
                        `;
                    }
                }
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def _websocket_handler(self, request):
        """معالج WebSocket مؤقت"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # رسالة ترحيب
        welcome_msg = {
            "type": "session.created",
            "session": {
                "id": "mock_session",
                "voice": "alloy",
                "instructions": "مرحباً! هذا محاكي مؤقت",
                "tools": []
            }
        }
        await ws.send_str(json.dumps(welcome_msg))
        
        # استمع للرسائل
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    response = await self._handle_message(data)
                    if response:
                        await ws.send_str(json.dumps(response))
                except Exception as e:
                    error_msg = {
                        "type": "error",
                        "message": f"خطأ: {str(e)}"
                    }
                    await ws.send_str(json.dumps(error_msg))
        
        return ws
    
    async def _handle_message(self, message):
        """معالجة الرسائل الواردة"""
        msg_type = message.get("type")
        
        if msg_type == "input_audio_buffer.append":
            # محاكاة استلام الصوت
            return {
                "type": "conversation.item.created",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "text", "text": "مرحباً، أريد بيتزا تونة وسط"}]
                }
            }
        
        elif msg_type == "response.create":
            # محاكاة الرد
            return {
                "type": "response.done",
                "response": {
                    "output": [
                        {
                            "type": "message",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": "مرحباً بك في مطعم سيركلز! بيتزا التونة الوسط متوفرة بسعر 85 جنيه. تحب تطلبها؟"
                                }
                            ]
                        }
                    ]
                }
            }
        
        return None

# دالة مساعدة لاختبار البحث
async def test_search_api(request):
    """API لاختبار البحث"""
    try:
        data = await request.json()
        query = data.get('query', '')
        
        # محاكاة نتيجة البحث
        mock_result = f"تم البحث عن: '{query}' - النتيجة: بيتزا التونة الوسط متوفرة بسعر 85 جنيه"
        
        return web.json_response({
            "success": True,
            "query": query,
            "result": mock_result
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)

# دالة لإضافة المحاكي للتطبيق
def add_mockup_to_app(app: web.Application):
    """إضافة المحاكي المؤقت للتطبيق"""
    mockup = RTMTMockup()
    mockup.attach_to_app(app)
    
    # إضافة API اختبار البحث
    app.router.add_post("/api/test-search", test_search_api)
    
    logger.info("🔧 تم تفعيل Real-time محاكي مؤقت")
    logger.info("🌐 اذهب إلى /test لاختبار النظام")
    
    return mockup
