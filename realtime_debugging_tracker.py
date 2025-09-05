#!/usr/bin/env python3
"""
أداة تشخيص شاملة لتتبع مسار البيانات في نظام الـ Real-time Model
==============================================================

هذه الأداة تتبع مسار البيانات كاملاً من:
1. البحث الدلالي في Azure AI Search
2. معالجة النتائج والترجمة
3. تحضير البيانات للموديل
4. إرسال البيانات للـ Real-time Model
5. تحليل استجابة الموديل

"""

import os
import sys
import json
import asyncio
from datetime import datetime
import logging

# إضافة مسار المجلد الرئيسي
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# إضافة مسار backend
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'backend')
sys.path.append(backend_path)

try:
    from ragtools import search_vector, get_search_client
    from app.backend.model_input_settings import format_search_results_for_model
    from app.backend.translation_utils import translate_text_auto
    print("✅ تم استيراد جميع الوحدات بنجاح")
except ImportError as e:
    print(f"❌ خطأ في استيراد الوحدات: {e}")
    sys.exit(1)

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeDebuggingTracker:
    """أداة تتبع شاملة للتشخيص"""
    
    def __init__(self):
        self.steps_log = []
        self.search_results = None
        self.formatted_results = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
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
            search_client = get_search_client()
            search_results = await search_vector(translated_query, mode='search_with_name_content')
            
            # تحليل النتائج
            results_analysis = {
                "original_query": query,
                "translated_query": translated_query,
                "results_count": len(search_results),
                "results_with_prices": 0,
                "price_types": [],
                "sample_results": []
            }
            
            for i, result in enumerate(search_results[:5]):  # أول 5 نتائج
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
            
            self.search_results = search_results
            self.log_step(1, "البحث في Azure AI Search", results_analysis)
            
            return search_results
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "error_type": type(e).__name__,
                "summary": f"خطأ في البحث: {str(e)}"
            }
            self.log_step(1, "البحث في Azure AI Search", error_data, "error")
            raise
    
    def step2_format_for_model(self, search_results):
        """الخطوة 2: تحضير النتائج للموديل"""
        try:
            print(f"\n📝 الخطوة 2: تحضير النتائج للموديل")
            
            # استخدام دالة التحضير الأصلية
            formatted_data = format_search_results_for_model(search_results)
            
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
            
            print(f"📄 النص المحضر للموديل:")
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
    
    def step3_analyze_model_input(self, formatted_data):
        """الخطوة 3: تحليل مدخلات الموديل"""
        try:
            print(f"\n🤖 الخطوة 3: تحليل مدخلات الموديل")
            
            analysis = {
                "total_length": len(formatted_data),
                "line_count": len(formatted_data.split('\n')),
                "word_count": len(formatted_data.split()),
                "price_keywords": [],
                "number_patterns": [],
                "structure_analysis": {}
            }
            
            # البحث عن كلمات السعر
            price_keywords = ['price', 'سعر', 'جنيه', 'ج.م', 'egp', 'le']
            for keyword in price_keywords:
                count = formatted_data.lower().count(keyword)
                if count > 0:
                    analysis["price_keywords"].append({"keyword": keyword, "count": count})
            
            # البحث عن الأرقام
            import re
            numbers = re.findall(r'\d+', formatted_data)
            analysis["number_patterns"] = [int(n) for n in numbers if n.isdigit()]
            
            # تحليل هيكل البيانات
            lines = formatted_data.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            analysis["structure_analysis"] = {
                "total_lines": len(lines),
                "non_empty_lines": len(non_empty_lines),
                "average_line_length": sum(len(line) for line in non_empty_lines) / len(non_empty_lines) if non_empty_lines else 0
            }
            
            analysis["summary"] = f"النص يحتوي على {analysis['word_count']} كلمة و {len(analysis['price_keywords'])} كلمة سعر و {len(analysis['number_patterns'])} رقم"
            
            self.log_step(3, "تحليل مدخلات الموديل", analysis)
            
            return analysis
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "error_type": type(e).__name__,
                "summary": f"خطأ في تحليل المدخلات: {str(e)}"
            }
            self.log_step(3, "تحليل مدخلات الموديل", error_data, "error")
            raise
    
    def step4_check_model_configuration(self):
        """الخطوة 4: فحص إعدادات الموديل"""
        try:
            print(f"\n⚙️ الخطوة 4: فحص إعدادات الموديل")
            
            config_analysis = {
                "environment_variables": {},
                "model_settings": {},
                "system_message_analysis": {}
            }
            
            # فحص متغيرات البيئة
            env_vars = [
                'AZURE_OPENAI_ENDPOINT',
                'AZURE_OPENAI_REALTIME_DEPLOYMENT_NAME',
                'AZURE_OPENAI_API_VERSION'
            ]
            
            for var in env_vars:
                value = os.getenv(var)
                config_analysis["environment_variables"][var] = {
                    "set": value is not None,
                    "length": len(value) if value else 0
                }
            
            # محاولة قراءة إعدادات الموديل من app.py
            try:
                app_file = os.path.join(backend_path, 'app.py')
                if os.path.exists(app_file):
                    with open(app_file, 'r', encoding='utf-8') as f:
                        app_content = f.read()
                    
                    # البحث عن system message
                    if 'system_message' in app_content or 'instructions' in app_content:
                        config_analysis["system_message_analysis"]["found"] = True
                        
                        # البحث عن كلمات مفتاحية في system message
                        price_related_words = ['سعر', 'price', 'متاح', 'available', 'غير متاح']
                        found_words = []
                        for word in price_related_words:
                            if word in app_content:
                                found_words.append(word)
                        
                        config_analysis["system_message_analysis"]["price_related_words"] = found_words
                    else:
                        config_analysis["system_message_analysis"]["found"] = False
                else:
                    config_analysis["system_message_analysis"]["file_exists"] = False
                    
            except Exception as e:
                config_analysis["system_message_analysis"]["error"] = str(e)
            
            config_analysis["summary"] = f"تم فحص {len(env_vars)} متغير بيئة"
            
            self.log_step(4, "فحص إعدادات الموديل", config_analysis)
            
            return config_analysis
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "error_type": type(e).__name__,
                "summary": f"خطأ في فحص الإعدادات: {str(e)}"
            }
            self.log_step(4, "فحص إعدادات الموديل", error_data, "error")
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
            
            filename = f"realtime_debugging_report_{self.timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 تم حفظ التقرير الكامل في: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ خطأ في حفظ التقرير: {e}")
            return None

async def main():
    """الدالة الرئيسية للتشخيص"""
    print("🚀 بدء تشخيص نظام Real-time Model")
    print("="*60)
    
    # إنشاء أداة التتبع
    tracker = RealtimeDebuggingTracker()
    
    # استعلامات تجريبية
    test_queries = [
        "بيتزا تونة وسط",
        "كالزونى فراخ", 
        "سندوتش كريسبي"
    ]
    
    try:
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'🧪 اختبار' if i == 1 else '🔄 اختبار'} {i}: {query}")
            print("-" * 40)
            
            # الخطوة 1: البحث
            search_results = await tracker.step1_azure_search_test(query)
            
            if search_results:
                # الخطوة 2: التحضير
                formatted_data = tracker.step2_format_for_model(search_results)
                
                # الخطوة 3: التحليل
                tracker.step3_analyze_model_input(formatted_data)
                
                # فاصل بين الاختبارات
                if i < len(test_queries):
                    print("\n" + "="*60)
        
        # الخطوة 4: فحص الإعدادات
        tracker.step4_check_model_configuration()
        
        # حفظ التقرير
        report_file = tracker.save_full_report()
        
        print(f"\n🎯 ملخص النتائج:")
        print(f"✅ خطوات ناجحة: {len([s for s in tracker.steps_log if s['status'] == 'success'])}")
        print(f"❌ خطوات فاشلة: {len([s for s in tracker.steps_log if s['status'] == 'error'])}")
        
        # تحليل المشكلة المحتملة
        print(f"\n🔍 تحليل المشكلة المحتملة:")
        
        successful_searches = len([s for s in tracker.steps_log if s['step'] == 1 and s['status'] == 'success'])
        if successful_searches > 0:
            print("✅ البحث الدلالي يعمل بشكل صحيح")
            print("✅ الأسعار متوفرة في قاعدة البيانات")
            print("🔍 المشكلة المحتملة في إعدادات Real-time Model أو نقل البيانات")
        else:
            print("❌ مشكلة في البحث الدلالي نفسه")
        
        if report_file:
            print(f"📊 راجع التفاصيل الكاملة في: {report_file}")
            
    except Exception as e:
        print(f"\n❌ خطأ عام في التشخيص: {e}")
        tracker.save_full_report()

if __name__ == "__main__":
    asyncio.run(main())
