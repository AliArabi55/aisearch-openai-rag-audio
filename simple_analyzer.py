#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محلل أداء مبسط يستخدم أدوات البحث الموجودة مباشرة
"""

import asyncio
import sys
import os
import time
import statistics
from datetime import datetime
import json

# إعداد الترميز
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# إضافة مسار backend للاستيراد
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

# تحميل متغيرات البيئة
load_dotenv()

class SimplePerformanceAnalyzer:
    def __init__(self):
        # قائمة الاستعلامات للاختبار
        self.test_queries = [
            {"query": "بيتزا تونه وسط", "expected_id": "107"},
            {"query": "كالزونى تونه وسط", "expected_id": "108"},
            {"query": "بيتزا تونه كبير", "expected_id": "109"},
            {"query": "بيتزا جمبري كبير", "expected_id": "110"},
            {"query": "بيتزا جمبري وسط", "expected_id": "111"},
            {"query": "بيتزا سبيا كبير", "expected_id": "112"},
            {"query": "بيتزا سبيا وسط", "expected_id": "113"},
            {"query": "بيتزا سي فود وسط", "expected_id": "114"},
            {"query": "بيتزا سي فود كبير", "expected_id": "115"},
            {"query": "بيتزا كابوريا كبير", "expected_id": "116"},
            {"query": "بيتزا كابوريا وسط", "expected_id": "117"},
            {"query": "بيتزا فسفور كبير", "expected_id": "118"},
            {"query": "كالزونى فسفور وسط", "expected_id": "119"}
        ]
        
        # إحصائيات الأداء
        self.search_times = []
        self.successful_searches = 0
        self.failed_searches = 0
        self.results = []
        
        # إعداد عميل البحث
        self.setup_search_client()
    
    def setup_search_client(self):
        """إعداد عميل البحث"""
        try:
            search_key = os.environ.get("AZURE_SEARCH_API_KEY")
            search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
            search_index = os.environ.get("AZURE_SEARCH_INDEX")
            
            if not all([search_key, search_endpoint, search_index]):
                print("⚠️ تحذير: متغيرات البيئة غير متوفرة - سيتم استخدام بيانات وهمية")
                self.search_client = None
                return
            
            credential = AzureKeyCredential(search_key)
            self.search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=search_index,
                credential=credential
            )
            print("✅ تم إعداد عميل البحث بنجاح")
            
        except Exception as e:
            print(f"❌ خطأ في إعداد البحث: {e}")
            self.search_client = None
    
    async def perform_search(self, query_text):
        """تنفيذ البحث وقياس الوقت"""
        start_time = time.time()
        
        try:
            if self.search_client:
                # بحث حقيقي في Azure
                search_results = self.search_client.search(
                    search_text=query_text,
                    top=5,
                    include_total_count=True
                )
                
                results = []
                async for result in search_results:
                    results.append(result)
                
                search_time = time.time() - start_time
                return search_time, results, None
            else:
                # محاكاة البحث للاختبار
                await asyncio.sleep(0.1 + (time.time() % 0.3))  # محاكاة زمن متغير
                search_time = time.time() - start_time
                
                # نتائج وهمية
                mock_results = [
                    {"ID": "107", "Name": "بيتزا تونه وسط", "Price": "150"},
                    {"ID": "108", "Name": "كالزونى تونه وسط", "Price": "140"},
                    {"ID": "109", "Name": "بيتزا تونه كبير", "Price": "185"}
                ]
                return search_time, mock_results, None
                
        except Exception as e:
            search_time = time.time() - start_time
            return search_time, [], str(e)
    
    async def test_query(self, query_data):
        """اختبار استعلام واحد"""
        query_text = query_data["query"]
        expected_id = query_data["expected_id"]
        
        print(f"🔍 اختبار: {query_text}")
        
        # تنفيذ البحث
        search_time, results, error = await self.perform_search(query_text)
        
        # تحليل النتائج
        found_item = None
        if results and not error:
            for result in results:
                if str(result.get("ID", "")) == expected_id:
                    found_item = result
                    break
        
        # تسجيل النتيجة
        test_result = {
            "query": query_text,
            "expected_id": expected_id,
            "search_time": search_time,
            "found": found_item is not None,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        if found_item:
            test_result["found_name"] = found_item.get("Name", "")
            test_result["found_price"] = found_item.get("Price", "")
            self.successful_searches += 1
            print(f"   ✅ وُجد: {found_item.get('Name', '')} في {search_time:.3f}s")
        else:
            self.failed_searches += 1
            if error:
                print(f"   ❌ خطأ: {error} ({search_time:.3f}s)")
            else:
                print(f"   ⚠️ لم يوجد الصنف المتوقع ({search_time:.3f}s)")
        
        self.search_times.append(search_time)
        self.results.append(test_result)
        
        return test_result
    
    def analyze_performance(self):
        """تحليل نتائج الأداء"""
        if not self.search_times:
            return "❌ لا توجد بيانات للتحليل"
        
        # الإحصائيات الأساسية
        avg_time = statistics.mean(self.search_times)
        median_time = statistics.median(self.search_times)
        min_time = min(self.search_times)
        max_time = max(self.search_times)
        std_dev = statistics.stdev(self.search_times) if len(self.search_times) > 1 else 0
        
        # تحديد الاستعلامات البطيئة
        slow_threshold = avg_time + std_dev
        slow_queries = [r for r in self.results if r["search_time"] > slow_threshold]
        
        # إنشاء التقرير
        report = f"""
🎯 تحليل أداء البحث في النظام (مدة دقيقتين)
{'='*55}

📊 إحصائيات عامة:
• إجمالي الاختبارات: {len(self.search_times)}
• عمليات البحث الناجحة: {self.successful_searches}
• عمليات البحث الفاشلة: {self.failed_searches}
• معدل النجاح: {(self.successful_searches/len(self.search_times)*100):.1f}%

⏱️ أوقات البحث:
• متوسط وقت البحث: {avg_time:.3f} ثانية
• الوسيط: {median_time:.3f} ثانية
• أسرع بحث: {min_time:.3f} ثانية
• أبطأ بحث: {max_time:.3f} ثانية
• الانحراف المعياري: {std_dev:.3f} ثانية

🔍 تفاصيل الاختبارات:
"""
        
        for i, result in enumerate(self.results, 1):
            status = "✅" if result["found"] else "❌" if result["error"] else "⚠️"
            query_short = result["query"][:25] + "..." if len(result["query"]) > 25 else result["query"]
            report += f"{i:2d}. {status} {query_short:<28} - {result['search_time']:.3f}s\n"
        
        # عمليات البحث البطيئة
        report += f"\n🐌 عمليات البحث البطيئة (أكثر من {slow_threshold:.3f} ثانية):\n"
        if slow_queries:
            for query in slow_queries:
                report += f"• {query['query']} - {query['search_time']:.3f} ثانية\n"
        else:
            report += "• لا توجد عمليات بحث بطيئة غير عادية\n"
        
        # التحليل والتوصيات
        report += f"""
🎯 تحليل الأداء:

1. سرعة البحث:
   • متوسط الاستجابة: {avg_time:.3f} ثانية
   • {'✅ سريع جداً (أقل من 0.2s)' if avg_time < 0.2 else '✅ سريع (0.2-0.5s)' if avg_time < 0.5 else '⚠️ مقبول (0.5-1s)' if avg_time < 1.0 else '❌ بطيء (أكثر من 1s)'}

2. استقرار الأداء:
   • الانحراف المعياري: {std_dev:.3f}
   • {'✅ مستقر' if std_dev < avg_time * 0.3 else '⚠️ متغير' if std_dev < avg_time * 0.6 else '❌ غير مستقر'}

3. دقة البحث:
   • معدل النجاح: {(self.successful_searches/len(self.search_times)*100):.1f}%
   • {'✅ ممتاز' if self.successful_searches/len(self.search_times) > 0.9 else '✅ جيد' if self.successful_searches/len(self.search_times) > 0.8 else '⚠️ يحتاج تحسين'}
"""
        
        # المشاكل المحتملة والحلول
        if avg_time > 0.5:
            report += "\n⚠️ تحليل البطء المحتمل:\n"
            report += "• شبكة الاتصال بـ Azure Search\n"
            report += "• حجم فهرس البحث (123 عنصر - مناسب)\n"
            report += "• معقدة استعلامات البحث\n"
        
        if self.failed_searches > 0:
            report += "\n🔧 اقتراحات التحسين:\n"
            report += "• مراجعة مطابقة النصوص العربية\n"
            report += "• تحسين معايير البحث\n"
            report += "• إضافة مرادفات للكلمات الشائعة\n"
        
        # أسباب بطء النموذج المحتملة
        report += f"""
        
🤖 تحليل أداء النموذج الإجمالي:

إذا كان النموذج يتأخر في الرد، فالأسباب المحتملة:

1. وقت البحث: {avg_time:.3f}s
   • {'✅ ليس سبب البطء' if avg_time < 0.5 else '⚠️ قد يساهم في البطء'}

2. معالجة النتائج:
   • يتم إرسال النتيجة الأولى فقط للنموذج (محسّن)
   • تنسيق النص مبسط

3. أسباب أخرى محتملة:
   • زمن استجابة نموذج Azure OpenAI
   • معالجة الصوت والتحويل
   • شبكة الاتصال
   • موارد الخادم

🔍 لتحديد السبب الدقيق، يُنصح بفحص:
• لوجات الخادم أثناء الاستخدام
• مراقبة استخدام وحدة المعالجة المركزية والذاكرة
• قياس أوقات كل مرحلة منفصلة
"""
        
        return report
    
    async def run_analysis(self, duration_minutes=2):
        """تشغيل التحليل"""
        print(f"🎯 بدء تحليل أداء البحث لمدة {duration_minutes} دقيقة")
        print(f"📝 سيتم اختبار {len(self.test_queries)} استعلام مختلف:\n")
        
        for i, query_data in enumerate(self.test_queries, 1):
            print(f"   {i:2d}. {query_data['query']} (ID: {query_data['expected_id']})")
        
        print(f"\n⏰ بدء التحليل...\n")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        query_index = 0
        cycle_count = 0
        
        while time.time() < end_time:
            # اختبار الاستعلام الحالي
            current_query = self.test_queries[query_index]
            await self.test_query(current_query)
            
            # الانتقال للاستعلام التالي
            query_index = (query_index + 1) % len(self.test_queries)
            if query_index == 0:
                cycle_count += 1
                print(f"\n🔄 تم إكمال الدورة {cycle_count}\n")
            
            # فترة انتظار قصيرة
            await asyncio.sleep(1)
        
        # إنشاء التقرير
        print("\n📊 تحليل النتائج...\n")
        report = self.analyze_performance()
        
        # حفظ النتائج
        with open('search_performance_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        with open('search_performance_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report

async def main():
    """الدالة الرئيسية"""
    analyzer = SimplePerformanceAnalyzer()
    
    try:
        report = await analyzer.run_analysis(duration_minutes=2)
        print(report)
        
        print("\n💾 تم حفظ التقرير في: search_performance_report.txt")
        print("💾 تم حفظ البيانات في: search_performance_results.json")
        
    except Exception as e:
        print(f"❌ خطأ في التحليل: {e}")

if __name__ == "__main__":
    asyncio.run(main())
