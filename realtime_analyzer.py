#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محلل أداء مباشر للتطبيق عبر WebSocket
يتصل مباشرة بالتطبيق ويقيس أوقات الاستجابة
"""

import asyncio
import websockets
import json
import time
import statistics
from datetime import datetime
import sys
import logging

# إعداد الترميز
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("realtime_analyzer")

class RealtimeModelAnalyzer:
    def __init__(self):
        # قائمة الأصناف المطلوب اختبارها
        self.test_queries = [
            "أريد بيتزا تونه وسط",
            "عايز كالزونى تونه وسط", 
            "أطلب بيتزا تونه كبير",
            "هات بيتزا جمبري كبير",
            "خد بيتزا جمبري وسط",
            "أريد بيتزا سبيا كبير",
            "عايز بيتزا سبيا وسط",
            "أطلب بيتزا سي فود وسط",
            "هات بيتزا سي فود كبير",
            "خد بيتزا كابوريا كبير",
            "أريد بيتزا كابوريا وسط",
            "عايز بيتزا فسفور كبير",
            "أطلب كالزونى فسفور وسط"
        ]
        
        # إحصائيات الأداء
        self.response_times = []
        self.successful_responses = 0
        self.failed_responses = 0
        self.analysis_results = []
        self.ws_url = "ws://localhost:8765/realtime"
        
    async def send_audio_query(self, websocket, query):
        """إرسال استعلام صوتي (محاكاة)"""
        try:
            # محاكاة إرسال استعلام صوتي
            # في التطبيق الحقيقي سيتم إرسال بيانات صوتية
            message = {
                "type": "input_audio_buffer.append",
                "audio": "fake_audio_data_for_" + query
            }
            
            await websocket.send(json.dumps(message))
            logger.info(f"📤 تم إرسال: {query}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في الإرسال: {e}")
            raise
    
    async def wait_for_response(self, websocket, timeout=10):
        """انتظار استجابة من النموذج"""
        start_time = time.time()
        response_received = False
        
        try:
            while time.time() - start_time < timeout:
                try:
                    # انتظار رسالة مع timeout قصير
                    message = await asyncio.wait_for(
                        websocket.recv(), 
                        timeout=1.0
                    )
                    
                    data = json.loads(message)
                    
                    # البحث عن استجابة صوتية أو نصية
                    if data.get("type") in ["response.audio.delta", "response.text.delta", "response.done"]:
                        response_time = time.time() - start_time
                        logger.info(f"📥 تم استلام رد في {response_time:.3f} ثانية")
                        return response_time, data
                        
                except asyncio.TimeoutError:
                    continue
                except json.JSONDecodeError:
                    continue
            
            # انتهت المدة المحددة بدون استجابة
            timeout_time = time.time() - start_time
            logger.warning(f"⏰ انتهت مدة الانتظار ({timeout_time:.3f} ثانية)")
            return timeout_time, {"type": "timeout"}
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ خطأ في انتظار الاستجابة: {e}")
            return error_time, {"type": "error", "error": str(e)}
    
    async def test_single_query(self, query):
        """اختبار استعلام واحد"""
        start_time = time.time()
        
        try:
            # الاتصال بالتطبيق
            async with websockets.connect(self.ws_url) as websocket:
                logger.info(f"🔗 متصل بالتطبيق: {query}")
                
                # إرسال الاستعلام
                await self.send_audio_query(websocket, query)
                
                # انتظار الاستجابة
                response_time, response_data = await self.wait_for_response(websocket)
                
                total_time = time.time() - start_time
                
                # تحليل النتيجة
                result = {
                    "query": query,
                    "response_time": response_time,
                    "total_time": total_time,
                    "response_type": response_data.get("type"),
                    "successful": response_data.get("type") not in ["timeout", "error"],
                    "timestamp": datetime.now().isoformat()
                }
                
                if result["successful"]:
                    self.successful_responses += 1
                    logger.info(f"✅ نجح: {query} - {total_time:.3f}s")
                else:
                    self.failed_responses += 1
                    logger.warning(f"❌ فشل: {query} - {response_data.get('type', 'unknown')}")
                
                self.response_times.append(total_time)
                self.analysis_results.append(result)
                
                return result
                
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ خطأ شامل في الاختبار: {e}")
            
            result = {
                "query": query,
                "error": str(e),
                "error_time": error_time,
                "successful": False,
                "timestamp": datetime.now().isoformat()
            }
            
            self.failed_responses += 1
            self.analysis_results.append(result)
            return result
    
    def generate_performance_report(self):
        """إنشاء تقرير الأداء"""
        if not self.response_times:
            return "❌ لا توجد بيانات للتحليل"
        
        # الإحصائيات الأساسية
        avg_time = statistics.mean(self.response_times)
        median_time = statistics.median(self.response_times)
        min_time = min(self.response_times)
        max_time = max(self.response_times)
        
        # تحديد الاستعلامات البطيئة
        slow_threshold = avg_time + statistics.stdev(self.response_times) if len(self.response_times) > 1 else avg_time * 1.5
        slow_queries = [r for r in self.analysis_results if r.get("total_time", 0) > slow_threshold]
        
        # إنشاء التقرير
        report = f"""
🎯 تحليل أداء النموذج الصوتي في الوقت الفعلي
{'='*60}

📊 إحصائيات عامة:
• إجمالي الاختبارات: {len(self.response_times)}
• الاستجابات الناجحة: {self.successful_responses}
• الاستجابات الفاشلة: {self.failed_responses}
• معدل النجاح: {(self.successful_responses/len(self.response_times)*100):.1f}%

⏱️ أوقات الاستجابة:
• متوسط وقت الاستجابة: {avg_time:.3f} ثانية
• الوسيط: {median_time:.3f} ثانية
• أسرع استجابة: {min_time:.3f} ثانية
• أبطأ استجابة: {max_time:.3f} ثانية

🔍 تفاصيل الاختبارات:
"""
        
        for i, result in enumerate(self.analysis_results, 1):
            status = "✅" if result["successful"] else "❌"
            time_str = f"{result.get('total_time', result.get('error_time', 0)):.3f}s"
            report += f"{i:2d}. {status} {result['query'][:30]:<30} - {time_str}\n"
        
        # الاستعلامات البطيئة
        report += f"\n🐌 الاستعلامات البطيئة (أكثر من {slow_threshold:.3f} ثانية):\n"
        if slow_queries:
            for query in slow_queries:
                report += f"• {query['query']} - {query.get('total_time', 0):.3f} ثانية\n"
        else:
            report += "• لا توجد استعلامات بطيئة غير عادية\n"
        
        # التحليل والتوصيات
        report += f"""
🎯 التحليل والتوصيات:

1. أداء النموذج:
   • متوسط الاستجابة: {avg_time:.3f} ثانية
   • {'✅ ممتاز (أقل من ثانية)' if avg_time < 1.0 else '✅ جيد (1-2 ثانية)' if avg_time < 2.0 else '⚠️ مقبول (2-3 ثواني)' if avg_time < 3.0 else '❌ بطيء (أكثر من 3 ثواني)'}

2. استقرار النظام:
   • معدل النجاح: {(self.successful_responses/len(self.response_times)*100):.1f}%
   • {'✅ مستقر' if self.successful_responses/len(self.response_times) > 0.8 else '⚠️ يحتاج تحسين'}

3. توزيع الأوقات:
   • الانحراف المعياري: {statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0:.3f}
   • {'✅ متسق' if (statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0) < avg_time * 0.5 else '⚠️ متغير'}
"""
        
        # اقتراحات التحسين
        if avg_time > 3.0:
            report += "\n🚀 اقتراحات تحسين الأداء:\n"
            report += "• فحص شبكة الإنترنت والاتصال بـ Azure\n"
            report += "• تحسين استعلامات البحث في قاعدة البيانات\n"
            report += "• زيادة موارد الخادم إذا أمكن\n"
            report += "• مراجعة إعدادات النموذج الصوتي\n"
        
        if self.failed_responses > len(self.response_times) * 0.2:
            report += "\n⚠️ اقتراحات تحسين الاستقرار:\n"
            report += "• فحص اتصال WebSocket\n"
            report += "• مراجعة معالجة الأخطاء\n"
            report += "• تحسين مهلة الانتظار (timeout)\n"
        
        return report
    
    async def run_analysis(self, duration_minutes=2):
        """تشغيل التحليل لمدة محددة"""
        logger.info(f"🎯 بدء تحليل الأداء لمدة {duration_minutes} دقيقة")
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        query_index = 0
        cycle_count = 0
        
        print(f"📝 سيتم اختبار {len(self.test_queries)} استعلام بالتناوب:")
        for i, query in enumerate(self.test_queries, 1):
            print(f"   {i:2d}. {query}")
        
        print(f"\n⏰ بدء التحليل لمدة {duration_minutes} دقيقة...\n")
        
        while time.time() < end_time:
            # اختيار الاستعلام الحالي
            current_query = self.test_queries[query_index]
            
            # تنفيذ الاختبار
            await self.test_single_query(current_query)
            
            # الانتقال للاستعلام التالي
            query_index = (query_index + 1) % len(self.test_queries)
            if query_index == 0:
                cycle_count += 1
                logger.info(f"🔄 تم إكمال الدورة {cycle_count}")
            
            # فترة انتظار بين الاختبارات
            await asyncio.sleep(3)
        
        # إنشاء التقرير
        report = self.generate_performance_report()
        
        # حفظ النتائج
        with open('realtime_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        with open('realtime_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report

async def main():
    """الدالة الرئيسية"""
    analyzer = RealtimeModelAnalyzer()
    
    try:
        # تشغيل التحليل
        report = await analyzer.run_analysis(duration_minutes=2)
        print(report)
        
        print("\n💾 تم حفظ التقرير في: realtime_analysis_report.txt")
        print("💾 تم حفظ البيانات الخام في: realtime_analysis_results.json")
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل التحليل: {e}")
        print(f"❌ خطأ شامل: {e}")

if __name__ == "__main__":
    asyncio.run(main())
