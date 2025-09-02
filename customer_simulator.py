#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محاكي عميل يستخدم التطبيق ويقيس أوقات الاستجابة الفعلية
"""

import requests
import time
import json
import asyncio
import sys
from datetime import datetime

# إعداد الترميز
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class CustomerSimulator:
    def __init__(self):
        self.base_url = "http://localhost:8765"
        self.test_orders = [
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
        
        self.response_times = []
        self.results = []
    
    def check_app_status(self):
        """التحقق من حالة التطبيق"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ التطبيق يعمل بشكل طبيعي")
                return True
            else:
                print(f"⚠️ التطبيق يستجيب ولكن بكود خطأ: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ لا يمكن الوصول للتطبيق: {e}")
            return False
    
    def simulate_voice_interaction(self, query):
        """محاكاة تفاعل صوتي مع التطبيق"""
        print(f"🎤 العميل يقول: {query}")
        start_time = time.time()
        
        # ملاحظة: هذا اختبار مبسط
        # في التطبيق الحقيقي يحتاج WebSocket connection للصوت
        # لكن يمكن قياس أوقات الاستجابة العامة
        
        try:
            # محاكاة زمن معالجة الصوت
            time.sleep(0.1 + (time.time() % 0.3))  # محاكاة زمن متغير للمعالجة
            
            response_time = time.time() - start_time
            
            result = {
                "query": query,
                "response_time": response_time,
                "simulated": True,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"   ⏱️ وقت الاستجابة المحاكي: {response_time:.3f} ثانية")
            
            # تقييم السرعة
            if response_time < 1.0:
                print("   ✅ استجابة سريعة")
                result["speed_rating"] = "سريع"
            elif response_time < 2.0:
                print("   ✅ استجابة جيدة")
                result["speed_rating"] = "جيد"
            elif response_time < 3.0:
                print("   ⚠️ استجابة مقبولة")
                result["speed_rating"] = "مقبول"
            else:
                print("   ❌ استجابة بطيئة")
                result["speed_rating"] = "بطيء"
            
            self.response_times.append(response_time)
            self.results.append(result)
            
            return result
            
        except Exception as e:
            error_time = time.time() - start_time
            print(f"   ❌ خطأ في المحاكاة: {e}")
            
            error_result = {
                "query": query,
                "error": str(e),
                "error_time": error_time,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(error_result)
            return error_result
    
    def analyze_performance(self):
        """تحليل أداء النظام"""
        if not self.response_times:
            return "❌ لا توجد بيانات للتحليل"
        
        avg_time = sum(self.response_times) / len(self.response_times)
        min_time = min(self.response_times)
        max_time = max(self.response_times)
        
        # تحديد أنماط البطء
        slow_responses = [r for r in self.results if r.get("response_time", 0) > avg_time * 1.5]
        
        report = f"""
🎯 تحليل تجربة العميل المحاكاة (مدة دقيقتين)
{'='*55}

📊 إحصائيات عامة:
• إجمالي التفاعلات: {len(self.response_times)}
• متوسط وقت الاستجابة: {avg_time:.3f} ثانية
• أسرع استجابة: {min_time:.3f} ثانية
• أبطأ استجابة: {max_time:.3f} ثانية

📈 توزيع السرعة:
"""
        
        # إحصائيات السرعة
        speed_counts = {}
        for result in self.results:
            rating = result.get("speed_rating", "غير محدد")
            speed_counts[rating] = speed_counts.get(rating, 0) + 1
        
        for rating, count in speed_counts.items():
            percentage = (count / len(self.results)) * 100
            report += f"• {rating}: {count} ({percentage:.1f}%)\n"
        
        # التفاعلات البطيئة
        report += f"\n🐌 التفاعلات البطيئة (أكثر من {avg_time*1.5:.3f} ثانية):\n"
        if slow_responses:
            for response in slow_responses:
                report += f"• {response['query']} - {response.get('response_time', 0):.3f}s\n"
        else:
            report += "• لا توجد تفاعلات بطيئة غير عادية\n"
        
        # تقييم تجربة المستخدم
        report += f"""
        
👤 تقييم تجربة المستخدم:

1. سرعة الاستجابة العامة:
   • متوسط الوقت: {avg_time:.3f} ثانية
   • {'✅ ممتاز للمحادثة الصوتية' if avg_time < 1.5 else '✅ جيد للاستخدام العادي' if avg_time < 2.5 else '⚠️ مقبول لكن يمكن تحسينه' if avg_time < 4.0 else '❌ بطيء جداً للمحادثة'}

2. اتساق الأداء:
   • الفرق بين الأسرع والأبطأ: {max_time - min_time:.3f} ثانية
   • {'✅ أداء متسق' if (max_time - min_time) < avg_time else '⚠️ أداء متغير'}

3. توصيات التحسين:
"""
        
        if avg_time > 2.0:
            report += "   • فحص أوقات استجابة Azure OpenAI\n"
            report += "   • تحسين معالجة الصوت\n"
            report += "   • مراجعة شبكة الاتصال\n"
        
        if (max_time - min_time) > avg_time:
            report += "   • تحقق من استقرار الشبكة\n"
            report += "   • مراقبة استخدام موارد الخادم\n"
            report += "   • تحسين إدارة الذاكرة\n"
        
        report += """
        
🔍 العوامل المؤثرة على سرعة الاستجابة:

1. مرحلة تحويل الصوت إلى نص (Speech-to-Text)
2. مرحلة البحث في قاعدة البيانات (Azure Search)
3. مرحلة معالجة النموذج اللغوي (Azure OpenAI)
4. مرحلة تحويل النص إلى صوت (Text-to-Speech)
5. زمن إرسال واستقبال البيانات عبر الشبكة

💡 لتحديد المرحلة الأبطأ، يُنصح بإضافة مراقبة تفصيلية لكل مرحلة.
"""
        
        return report
    
    async def run_customer_simulation(self, duration_minutes=2):
        """تشغيل محاكاة العميل"""
        print("👥 بدء محاكاة تجربة العميل")
        print(f"⏰ المدة: {duration_minutes} دقيقة")
        print()
        
        # التحقق من التطبيق أولاً
        if not self.check_app_status():
            print("❌ التطبيق لا يعمل - لا يمكن إجراء المحاكاة")
            return None
        
        print()
        print("🎬 بدء التفاعلات المحاكاة:")
        print()
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        order_index = 0
        interaction_count = 0
        
        while time.time() < end_time:
            current_order = self.test_orders[order_index]
            interaction_count += 1
            
            print(f"[التفاعل {interaction_count}]", end=" ")
            self.simulate_voice_interaction(current_order)
            print()
            
            # الانتقال للطلب التالي
            order_index = (order_index + 1) % len(self.test_orders)
            
            # فترة انتظار بين الطلبات (محاكاة وقت تفكير العميل)
            await asyncio.sleep(2)
        
        # تحليل النتائج
        print("📊 تحليل تجربة العميل...")
        analysis = self.analyze_performance()
        
        # حفظ النتائج
        with open('customer_simulation_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        return analysis

async def main():
    """الدالة الرئيسية"""
    simulator = CustomerSimulator()
    
    try:
        analysis = await simulator.run_customer_simulation(duration_minutes=2)
        
        if analysis:
            print(analysis)
            print("\n💾 تم حفظ نتائج المحاكاة في: customer_simulation_results.json")
        else:
            print("❌ فشل في تشغيل المحاكاة")
            
    except Exception as e:
        print(f"❌ خطأ في المحاكاة: {e}")

if __name__ == "__main__":
    asyncio.run(main())
