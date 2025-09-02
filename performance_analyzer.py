#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة تحليل أداء النموذج الصوتي في الوقت الفعلي
تحاكي عميل يطلب أصناف مختلفة وتقيس أوقات الاستجابة
"""

import asyncio
import time
import json
import logging
from datetime import datetime
import statistics
import sys
import os

# إعداد الترميز
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# إعداد المسارات
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

# استيراد أدوات البحث
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient as AzureSearchClient
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('performance_analysis.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("performance_analyzer")

class PerformanceAnalyzer:
    def __init__(self):
        # قائمة الأصناف المطلوب اختبارها
        self.test_items = [
            {"id": 107, "name": "بيتزا تونه وسط", "price": 150, "query": "أريد بيتزا تونه وسط"},
            {"id": 108, "name": "كالزونى تونه وسط", "price": 140, "query": "عايز كالزونى تونه وسط"},
            {"id": 109, "name": "بيتزا تونه كبير", "price": 185, "query": "أطلب بيتزا تونه كبير"},
            {"id": 110, "name": "بيتزا جمبري كبير", "price": 195, "query": "هات بيتزا جمبري كبير"},
            {"id": 111, "name": "بيتزا جمبري وسط", "price": 170, "query": "خد بيتزا جمبري وسط"},
            {"id": 112, "name": "بيتزا سبيا كبير", "price": 195, "query": "أريد بيتزا سبيا كبير"},
            {"id": 113, "name": "بيتزا سبيا وسط", "price": 170, "query": "عايز بيتزا سبيا وسط"},
            {"id": 114, "name": "بيتزا سي فود وسط", "price": 185, "query": "أطلب بيتزا سي فود وسط"},
            {"id": 115, "name": "بيتزا سي فود كبير", "price": 210, "query": "هات بيتزا سي فود كبير"},
            {"id": 116, "name": "بيتزا كابوريا كبير", "price": 175, "query": "خد بيتزا كابوريا كبير"},
            {"id": 117, "name": "بيتزا كابوريا وسط", "price": 140, "query": "أريد بيتزا كابوريا وسط"},
            {"id": 118, "name": "بيتزا فسفور كبير", "price": 220, "query": "عايز بيتزا فسفور كبير"},
            {"id": 119, "name": "كالزونى فسفور وسط", "price": 165, "query": "أطلب كالزونى فسفور وسط"}
        ]
        
        # إحصائيات الأداء
        self.response_times = []
        self.search_times = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.analysis_results = []
        
        # إعداد عميل البحث
        self.setup_search_client()
    
    def setup_search_client(self):
        """إعداد عميل البحث في Azure"""
        try:
            search_key = os.environ.get("AZURE_SEARCH_API_KEY")
            search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
            search_index = os.environ.get("AZURE_SEARCH_INDEX")
            
            if not all([search_key, search_endpoint, search_index]):
                raise ValueError("متغيرات البيئة المطلوبة غير موجودة")
            
            credential = AzureKeyCredential(search_key)
            self.search_client = AzureSearchClient(
                endpoint=search_endpoint,
                index_name=search_index,
                credential=credential
            )
            logger.info("✅ تم إعداد عميل البحث بنجاح")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إعداد عميل البحث: {e}")
            self.search_client = None
    
    async def test_search_performance(self, query, expected_item):
        """اختبار أداء البحث لصنف واحد"""
        start_time = time.time()
        
        try:
            # محاكاة البحث
            logger.info(f"🔍 البحث عن: {query}")
            
            if not self.search_client:
                raise Exception("عميل البحث غير متاح")
            
            # تنفيذ البحث الفعلي
            search_start = time.time()
            results = await self.search_client.search(
                search_text=query,
                top=5,
                include_total_count=True
            )
            
            # تحويل النتائج إلى قائمة
            results_list = []
            async for result in results:
                results_list.append(result)
            
            search_time = time.time() - search_start
            
            # تحليل النتائج
            found_item = None
            if results_list and len(results_list) > 0:
                for result in results_list:
                    if str(expected_item["id"]) in str(result.get("ID", "")):
                        found_item = result
                        break
            
            total_time = time.time() - start_time
            
            # تسجيل النتائج
            result_data = {
                "query": query,
                "expected_id": expected_item["id"],
                "expected_name": expected_item["name"],
                "search_time": search_time,
                "total_time": total_time,
                "found": found_item is not None,
                "timestamp": datetime.now().isoformat()
            }
            
            if found_item:
                result_data["found_name"] = found_item.get("Name", "")
                result_data["found_price"] = found_item.get("Price", "")
                self.successful_requests += 1
                logger.info(f"✅ تم العثور على: {found_item.get('Name')} في {total_time:.3f} ثانية")
            else:
                self.failed_requests += 1
                logger.warning(f"❌ لم يتم العثور على الصنف المتوقع: {expected_item['name']}")
            
            self.response_times.append(total_time)
            self.search_times.append(search_time)
            self.analysis_results.append(result_data)
            
            return result_data
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ خطأ في البحث: {e} (وقت الخطأ: {error_time:.3f})")
            self.failed_requests += 1
            return {
                "query": query,
                "error": str(e),
                "error_time": error_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_performance_patterns(self):
        """تحليل أنماط الأداء"""
        if not self.response_times:
            return "❌ لا توجد بيانات كافية للتحليل"
        
        # الإحصائيات الأساسية
        avg_response = statistics.mean(self.response_times)
        median_response = statistics.median(self.response_times)
        min_response = min(self.response_times)
        max_response = max(self.response_times)
        
        # إحصائيات البحث
        avg_search = statistics.mean(self.search_times) if self.search_times else 0
        
        # تحديد الاستعلامات البطيئة
        slow_threshold = avg_response + (2 * statistics.stdev(self.response_times)) if len(self.response_times) > 1 else avg_response * 1.5
        slow_queries = [r for r in self.analysis_results if r.get("total_time", 0) > slow_threshold]
        
        analysis = f"""
📊 تحليل أداء النموذج لمدة دقيقتين
{'='*50}

📈 إحصائيات عامة:
• إجمالي الطلبات: {len(self.response_times)}
• الطلبات الناجحة: {self.successful_requests}
• الطلبات الفاشلة: {self.failed_requests}
• معدل النجاح: {(self.successful_requests/len(self.response_times)*100):.1f}%

⏱️ أوقات الاستجابة:
• متوسط وقت الاستجابة: {avg_response:.3f} ثانية
• الوسيط: {median_response:.3f} ثانية
• أسرع استجابة: {min_response:.3f} ثانية
• أبطأ استجابة: {max_response:.3f} ثانية
• متوسط وقت البحث: {avg_search:.3f} ثانية

🐌 الاستعلامات البطيئة (أكثر من {slow_threshold:.3f} ثانية):
"""
        
        if slow_queries:
            for query in slow_queries:
                analysis += f"• {query['query']} - {query.get('total_time', 0):.3f} ثانية\n"
        else:
            analysis += "• لا توجد استعلامات بطيئة غير عادية\n"
        
        # تحليل الأسباب المحتملة للبطء
        analysis += f"""
🔍 التحليل والتوصيات:

1. أداء البحث في Azure:
   • متوسط وقت البحث: {avg_search:.3f} ثانية
   • {'✅ جيد' if avg_search < 0.5 else '⚠️ يحتاج تحسين' if avg_search < 1.0 else '❌ بطيء'}

2. أداء النموذج العام:
   • متوسط الاستجابة: {avg_response:.3f} ثانية
   • {'✅ ممتاز' if avg_response < 1.0 else '✅ جيد' if avg_response < 2.0 else '⚠️ مقبول' if avg_response < 3.0 else '❌ بطيء'}

3. نسبة النجاح:
   • معدل النجاح: {(self.successful_requests/len(self.response_times)*100):.1f}%
   • {'✅ ممتاز' if self.successful_requests/len(self.response_times) > 0.9 else '⚠️ يحتاج تحسين'}
"""

        # اقتراحات التحسين
        if avg_response > 2.0:
            analysis += "\n🚀 اقتراحات لتحسين الأداء:\n"
            analysis += "• تحسين استعلامات البحث\n"
            analysis += "• زيادة موارد الخادم\n"
            analysis += "• تحسين خوارزمية البحث\n"
        
        if self.failed_requests > 0:
            analysis += "\n⚠️ اقتراحات لتحسين دقة البحث:\n"
            analysis += "• مراجعة مؤشر البحث\n"
            analysis += "• تحسين معايير البحث\n"
            analysis += "• إضافة معالجة أفضل للأخطاء\n"
        
        return analysis
    
    async def run_analysis(self, duration_minutes=2):
        """تشغيل التحليل لمدة محددة"""
        logger.info(f"🎯 بدء تحليل الأداء لمدة {duration_minutes} دقيقة")
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        item_index = 0
        cycle_count = 0
        
        while time.time() < end_time:
            # اختيار الصنف الحالي
            current_item = self.test_items[item_index]
            
            # تنفيذ الاختبار
            result = await self.test_search_performance(
                current_item["query"], 
                current_item
            )
            
            # الانتقال للصنف التالي
            item_index = (item_index + 1) % len(self.test_items)
            if item_index == 0:
                cycle_count += 1
                logger.info(f"🔄 تم إكمال الدورة {cycle_count}")
            
            # فترة انتظار قصيرة بين الطلبات
            await asyncio.sleep(2)
        
        # تحليل النتائج
        logger.info("📊 تحليل النتائج...")
        analysis = self.analyze_performance_patterns()
        
        # حفظ النتائج
        with open('performance_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        return analysis

# Mock SearchClient for testing (هذا فقط للمرجع - لن يتم استخدامه)
class MockSearchClient:
    def __init__(self, endpoint, index_name, credential):
        self.endpoint = endpoint
        self.index_name = index_name
        self.credential = credential
    
    async def search(self, search_text, top=5, include_total_count=True):
        """محاكاة البحث - في التطبيق الفعلي سيتم استخدام Azure Search"""
        await asyncio.sleep(0.2)  # محاكاة زمن البحث
        
        # بيانات وهمية للاختبار
        mock_results = [
            {"ID": "107", "Name": "بيتزا تونه وسط", "Price": "150"},
            {"ID": "108", "Name": "كالزونى تونه وسط", "Price": "140"},
            {"ID": "109", "Name": "بيتزا تونه كبير", "Price": "185"},
        ]
        
        for result in mock_results:
            yield result

async def main():
    """الدالة الرئيسية لتشغيل التحليل"""
    analyzer = PerformanceAnalyzer()
    
    print("🎯 بدء تحليل أداء النموذج...")
    print("📝 سيتم اختبار الأصناف التالية بالترتيب:")
    
    for item in analyzer.test_items:
        print(f"   • {item['name']} ({item['query']})")
    
    print("\n⏰ بدء التحليل لمدة دقيقتين...")
    
    try:
        analysis_result = await analyzer.run_analysis(duration_minutes=2)
        print(analysis_result)
        
        # حفظ التحليل في ملف
        with open('performance_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(analysis_result)
        
        print("\n💾 تم حفظ التقرير في: performance_analysis_report.txt")
        print("💾 تم حفظ البيانات الخام في: performance_analysis_results.json")
        
    except Exception as e:
        logger.error(f"❌ خطأ في التحليل: {e}")
        print(f"❌ خطأ في تشغيل التحليل: {e}")

if __name__ == "__main__":
    asyncio.run(main())
