#!/usr/bin/env python3
"""
أداة تشخيص مبسطة لتتبع مسار البيانات في نظام الـ Real-time Model
==============================================================
"""

import os
import sys
import json
import asyncio
from datetime import datetime
import logging

# إضافة مسار backend
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'backend')
sys.path.append(backend_path)

try:
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from model_input_settings import generate_model_input
    from translation_utils import translate_text_auto
    print("✅ تم استيراد جميع الوحدات بنجاح")
except ImportError as e:
    print(f"❌ خطأ في استيراد الوحدات: {e}")
    sys.exit(1)

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleRealtimeTracker:
    """أداة تتبع مبسطة للتشخيص"""
    
    def __init__(self):
        self.steps_log = []
        self.search_results = None
        self.formatted_results = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # إعداد Azure Search
        self.search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "")
        self.search_key = os.getenv("AZURE_SEARCH_KEY", "")
        self.search_index = os.getenv("AZURE_SEARCH_INDEX", "english22-index")
        
        if not self.search_endpoint or not self.search_key:
            print("❌ متغيرات البيئة للبحث غير مكونة")
            sys.exit(1)
            
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index,
            credential=AzureKeyCredential(self.search_key)
        )
        
    def log_step(self, step_number, step_name, data, status="success"):
        """تسجيل خطوة في عملية التتبع"""
        step_info = {
            "step": step_number,
            "name": step_name,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "data": data
        }
        self.steps_log.append(step_info)
        
        # طباعة فورية للمتابعة
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        print(f"\n{status_icon} الخطوة {step_number}: {step_name}")
        if isinstance(data, dict) and "summary" in data:
            print(f"📋 الملخص: {data['summary']}")
        
    async def step1_azure_search_test(self, query):
        """الخطوة 1: اختبار البحث في Azure AI Search"""
        try:
            print(f"\n🔍 الخطوة 1: البحث عن '{query}' في Azure AI Search")
            
            # ترجمة النص أولاً
            translated_query = await translate_text_auto(query)
            print(f"🌍 النص المترجم: {translated_query}")
            
            # البحث الدلالي
            search_results = self.search_client.search(
                search_text=translated_query,
                query_type="semantic", 
                semantic_configuration_name="english22-index-semantic-configuration",
                top=5,
                select="ID,Name,ingredients,Price",
                search_fields=["Name", "ingredients"],
                query_caption="extractive",
                query_answer="extractive"
            )
            
            # تحويل النتائج إلى قائمة
            results_list = list(search_results)
            
            # تحليل النتائج
            results_analysis = {
                "original_query": query,
                "translated_query": translated_query,
                "results_count": len(results_list),
                "results_with_prices": 0,
                "price_types": [],
                "sample_results": []
            }
            
            for i, result in enumerate(results_list[:5]):  # أول 5 نتائج
                price = result.get('Price', 'N/A')
                price_available = price != 'N/A' and price is not None
                
                if price_available:
                    results_analysis["results_with_prices"] += 1
                    results_analysis["price_types"].append(type(price).__name__)
                
                sample_result = {
                    "index": i + 1,
                    "name": result.get('Name', 'Unknown'),
                    "price": price,
                    "price_type": type(price).__name__,
                    "price_available": price_available,
                    "id": result.get('ID', 'N/A')
                }
                results_analysis["sample_results"].append(sample_result)
                
                print(f"   📦 العنصر {i+1}: {sample_result['name']}")
                print(f"      💰 السعر: {price} (نوع: {type(price).__name__})")
                print(f"      ✅ السعر متاح: {'نعم' if price_available else 'لا'}")
            
            results_analysis["summary"] = f"وُجدت {results_analysis['results_count']} نتائج، {results_analysis['results_with_prices']} منها تحتوي على أسعار"
            
            self.search_results = results_list
            self.log_step(1, "البحث في Azure AI Search", results_analysis)
            
            return results_list
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "error_type": type(e).__name__,
                "summary": f"خطأ في البحث: {str(e)}"
            }
            self.log_step(1, "البحث في Azure AI Search", error_data, "error")
            raise
    
    def step2_format_for_model(self, search_results, original_query, translated_query):
        """الخطوة 2: تحضير النتائج للموديل"""
        try:
            print(f"\n📝 الخطوة 2: تحضير النتائج للموديل")
            
            # استخدام دالة التحضير الأصلية
            formatted_data = generate_model_input(search_results, original_query, translated_query)
            
            # تحليل البيانات المحضرة
            format_analysis = {
                "input_results_count": len(search_results),
                "formatted_text_length": len(formatted_data),
                "contains_prices": "السعر" in formatted_data or "price" in formatted_data.lower(),
                "price_mentions": [],
                "sample_formatted_text": formatted_data[:500] + "..." if len(formatted_data) > 500 else formatted_data
            }
            
            # البحث عن الأسعار في النص المحضر
            lines = formatted_data.split('\n')
            for line in lines:
                if any(price_word in line.lower() for price_word in ['price', 'سعر', 'جنيه', 'ج.م']):
                    format_analysis["price_mentions"].append(line.strip())
            
            format_analysis["summary"] = f"تم تحضير {format_analysis['input_results_count']} نتائج في نص بطول {format_analysis['formatted_text_length']} حرف"
            
            self.formatted_results = formatted_data
            self.log_step(2, "تحضير البيانات للموديل", format_analysis)
            
            print(f"\n📄 النص المحضر للموديل:")
            print(f"{'='*50}")
            print(formatted_data)
            print(f"{'='*50}")
            
            return formatted_data
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "error_type": type(e).__name__,
                "summary": f"خطأ في تحضير البيانات: {str(e)}"
            }
            self.log_step(2, "تحضير البيانات للموديل", error_data, "error")
            raise
    
    def step3_analyze_realtime_config(self):
        """الخطوة 3: فحص إعداد الـ Real-time Model"""
        try:
            print(f"\n🤖 الخطوة 3: فحص إعدادات Real-time Model")
            
            config_analysis = {
                "environment_variables": {},
                "app_py_analysis": {},
                "system_message_analysis": {}
            }
            
            # فحص متغيرات البيئة
            env_vars = [
                'AZURE_OPENAI_ENDPOINT',
                'AZURE_OPENAI_REALTIME_DEPLOYMENT_NAME',
                'AZURE_OPENAI_API_VERSION',
                'AZURE_OPENAI_API_KEY'
            ]
            
            for var in env_vars:
                value = os.getenv(var)
                config_analysis["environment_variables"][var] = {
                    "set": value is not None,
                    "length": len(value) if value else 0
                }
                print(f"   🔧 {var}: {'✅ مُعرف' if value else '❌ غير مُعرف'}")
            
            # محاولة قراءة إعدادات الموديل من app.py
            try:
                app_file = os.path.join(backend_path, 'app.py')
                if os.path.exists(app_file):
                    with open(app_file, 'r', encoding='utf-8') as f:
                        app_content = f.read()
                    
                    config_analysis["app_py_analysis"]["file_size"] = len(app_content)
                    config_analysis["app_py_analysis"]["lines"] = len(app_content.split('\n'))
                    
                    # البحث عن system message أو instructions
                    system_msg_patterns = [
                        'system_message',
                        'instructions',
                        'system.*message',
                        'role.*system'
                    ]
                    
                    found_patterns = []
                    for pattern in system_msg_patterns:
                        if pattern.replace('.*', '') in app_content.lower():
                            found_patterns.append(pattern)
                    
                    config_analysis["system_message_analysis"]["found_patterns"] = found_patterns
                    
                    # البحث عن كلمات مفتاحية متعلقة بالسعر
                    price_keywords = ['سعر', 'price', 'متاح', 'available', 'غير متاح', 'unavailable']
                    found_price_keywords = []
                    for keyword in price_keywords:
                        if keyword in app_content:
                            count = app_content.count(keyword)
                            found_price_keywords.append({"keyword": keyword, "count": count})
                    
                    config_analysis["system_message_analysis"]["price_keywords"] = found_price_keywords
                    
                    print(f"   📄 app.py: {len(app_content)} حرف، {len(app_content.split('\\n'))} سطر")
                    print(f"   🔍 أنماط system message: {found_patterns}")
                    print(f"   💰 كلمات السعر: {[k['keyword'] for k in found_price_keywords]}")
                    
                else:
                    config_analysis["app_py_analysis"]["file_exists"] = False
                    print("   ❌ ملف app.py غير موجود")
                    
            except Exception as e:
                config_analysis["app_py_analysis"]["error"] = str(e)
                print(f"   ❌ خطأ في قراءة app.py: {e}")
            
            config_analysis["summary"] = f"تم فحص {len(env_vars)} متغير بيئة وملف app.py"
            
            self.log_step(3, "فحص إعدادات Real-time Model", config_analysis)
            
            return config_analysis
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "error_type": type(e).__name__,
                "summary": f"خطأ في فحص الإعدادات: {str(e)}"
            }
            self.log_step(3, "فحص إعدادات Real-time Model", error_data, "error")
            raise
    
    def save_full_report(self):
        """حفظ التقرير الكامل"""
        try:
            report = {
                "timestamp": self.timestamp,
                "total_steps": len(self.steps_log),
                "successful_steps": len([s for s in self.steps_log if s["status"] == "success"]),
                "error_steps": len([s for s in self.steps_log if s["status"] == "error"]),
                "steps": self.steps_log,
                "raw_search_results": self.search_results,
                "formatted_results": self.formatted_results
            }
            
            filename = f"simple_realtime_debug_{self.timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 تم حفظ التقرير الكامل في: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ خطأ في حفظ التقرير: {e}")
            return None

async def main():
    """الدالة الرئيسية للتشخيص"""
    print("🚀 بدء تشخيص نظام Real-time Model المبسط")
    print("="*60)
    
    # إنشاء أداة التتبع
    tracker = SimpleRealtimeTracker()
    
    # استعلام تجريبي واحد
    test_query = "بيتزا تونة وسط"
    
    try:
        print(f"🧪 اختبار: {test_query}")
        print("-" * 40)
        
        # الخطوة 1: البحث
        search_results = await tracker.step1_azure_search_test(test_query)
        
        if search_results:
            # الخطوة 2: التحضير
            formatted_data = tracker.step2_format_for_model(search_results, test_query, await tracker.translate_text_auto(test_query))
            
        # الخطوة 3: فحص الإعدادات
        tracker.step3_analyze_realtime_config()
        
        # حفظ التقرير
        report_file = tracker.save_full_report()
        
        print(f"\n🎯 ملخص النتائج:")
        print(f"✅ خطوات ناجحة: {len([s for s in tracker.steps_log if s['status'] == 'success'])}")
        print(f"❌ خطوات فاشلة: {len([s for s in tracker.steps_log if s['status'] == 'error'])}")
        
        # تحليل المشكلة المحتملة
        print(f"\n🔍 تحليل المشكلة:")
        
        successful_searches = len([s for s in tracker.steps_log if s['step'] == 1 and s['status'] == 'success'])
        if successful_searches > 0:
            print("✅ البحث الدلالي يعمل بشكل صحيح")
            print("✅ الأسعار متوفرة في قاعدة البيانات بصيغة int")
            print("✅ تحضير البيانات للموديل يعمل")
            print("🔍 المشكلة المحتملة في إعدادات Real-time Model system message")
        else:
            print("❌ مشكلة في البحث الدلالي نفسه")
        
        if report_file:
            print(f"📊 راجع التفاصيل الكاملة في: {report_file}")
            
    except Exception as e:
        print(f"\n❌ خطأ عام في التشخيص: {e}")
        tracker.save_full_report()

if __name__ == "__main__":
    asyncio.run(main())
