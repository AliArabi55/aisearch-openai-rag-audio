#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مراقب العمليات في الوقت الفعلي
Real-time Operations Monitor
"""

import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class RealtimeMonitor:
    """مراقب العمليات في Real-time"""
    
    def __init__(self):
        self.websocket = None
        self.is_connected = False
    
    async def connect(self):
        """الاتصال بـ Real-time WebSocket"""
        try:
            self.websocket = await websockets.connect(
                "ws://localhost:8765/realtime",
                extra_headers={
                    "Authorization": "Bearer dummy",
                    "OpenAI-Beta": "realtime=v1"
                }
            )
            self.is_connected = True
            logger.info("🔗 تم الاتصال بـ Real-time WebSocket")
            
        except Exception as e:
            logger.error(f"❌ فشل الاتصال: {e}")
    
    async def send_arabic_message(self, message: str):
        """إرسال رسالة عربية وعرض المعالجة"""
        if not self.is_connected:
            await self.connect()
        
        logger.info(f"📤 إرسال: {message}")
        
        # إعداد جلسة Real-time
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "أنت مساعد ذكي لمطعم عربي. ساعد العملاء في طلب الطعام.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                },
                "tools": [],
                "tool_choice": "auto",
                "temperature": 0.8,
                "max_response_output_tokens": 4096
            }
        }
        
        await self.websocket.send(json.dumps(session_config))
        
        # إرسال النص
        text_message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": message
                    }
                ]
            }
        }
        
        await self.websocket.send(json.dumps(text_message))
        
        # طلب الرد
        response_create = {
            "type": "response.create",
            "response": {
                "modalities": ["text"],
                "instructions": "اجب باللغة العربية فقط"
            }
        }
        
        await self.websocket.send(json.dumps(response_create))
        
        # مراقبة الردود
        await self.monitor_responses()
    
    async def monitor_responses(self):
        """مراقبة الردود وعرض العمليات"""
        logger.info("👁️ بدء مراقبة العمليات...")
        
        try:
            while True:
                response = await self.websocket.recv()
                data = json.loads(response)
                
                event_type = data.get("type", "unknown")
                
                if event_type == "session.created":
                    logger.info("✅ تم إنشاء الجلسة")
                
                elif event_type == "session.updated":
                    logger.info("🔄 تم تحديث الجلسة")
                
                elif event_type == "conversation.item.created":
                    logger.info("📝 تم إنشاء عنصر في المحادثة")
                
                elif event_type == "response.created":
                    logger.info("🤖 بدء إنشاء الرد")
                
                elif event_type == "response.output_item.added":
                    item = data.get("item", {})
                    logger.info(f"➕ إضافة عنصر الرد: {item.get('type', 'unknown')}")
                
                elif event_type == "response.content_part.added":
                    part = data.get("part", {})
                    logger.info(f"📄 إضافة جزء المحتوى: {part.get('type', 'unknown')}")
                
                elif event_type == "response.content_part.done":
                    part = data.get("part", {})
                    if part.get("type") == "text":
                        text = part.get("text", "")
                        logger.info(f"✅ نص الرد: {text}")
                
                elif event_type == "response.done":
                    logger.info("🏁 انتهى الرد")
                    break
                
                elif event_type == "error":
                    error = data.get("error", {})
                    logger.error(f"❌ خطأ: {error}")
                    break
                
                else:
                    logger.debug(f"🔍 حدث آخر: {event_type}")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في المراقبة: {e}")

async def main():
    """الدالة الرئيسية"""
    monitor = RealtimeMonitor()
    
    # رسائل تجريبية
    test_messages = [
        "أريد بيتزا تونة وسط",
        "ما هي الأصناف المتاحة؟",
        "كم سعر البيتزا الكبيرة؟"
    ]
    
    for message in test_messages:
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 اختبار الرسالة: {message}")
        logger.info(f"{'='*60}")
        
        try:
            await monitor.send_arabic_message(message)
            await asyncio.sleep(2)  # فترة انتظار بين الرسائل
        
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال الرسالة: {e}")
        
        logger.info(f"{'='*60}\n")

if __name__ == "__main__":
    print("🚀 بدء مراقب العمليات في Real-time")
    print("🔗 سيتم الاتصال بـ localhost:8765")
    print("👁️ سيتم عرض جميع العمليات والترجمات والبحث")
    print("-" * 60)
    
    asyncio.run(main())
