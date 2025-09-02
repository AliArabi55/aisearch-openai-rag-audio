#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار البحث الحقيقي مع Azure Search لقياس الأداء الفعلي
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime

# إعداد الترميز
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# إضافة مسار backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from dotenv import load_dotenv
from ragtools import _search_tool  # استخدام أداة البحث من ragtools مباشرة

load_dotenv()

class RealSearchTester:
    def __init__(self):
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
        
        self.results = []
        self.search_times = []
    
    async def test_search_function(self, query):
        """اختبار دالة البحث الحقيقية"""
        print(f"🔍 اختبار: {query}")
        start_time = time.time()
        
        try:
            # استخدام دالة البحث الحقيقية من ragtools
            result = await _search_tool(query)
            
            search_time = time.time() - start_time
            
            # تحليل النتيجة
            result_data = {
                "query": query,
                "search_time": search_time,
                "result_text": result if result else "لا توجد نتائج",
                "successful": bool(result),
                "timestamp": datetime.now().isoformat()
            }
            
            if result:
                print(f"   ✅ النتيجة: {result[:100]}..." if len(result) > 100 else f"   ✅ النتيجة: {result}")
                print(f"   ⏱️ الوقت: {search_time:.3f} ثانية")
            else:
                print(f"   ❌ لا توجد نتائج")
                print(f"   ⏱️ الوقت: {search_time:.3f} ثانية")
            
            self.search_times.append(search_time)
            self.results.append(result_data)
            
            return result_data
            
        except Exception as e:
            error_time = time.time() - start_time
            print(f"   ❌ خطأ: {e}")
            print(f"   ⏱️ وقت الخطأ: {error_time:.3f} ثانية")
            
            error_data = {
                "query": query,
                "search_time": error_time,
                "error": str(e),
                "successful": False,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(error_data)
            return error_data
    
    async def run_quick_test(self):
        """تشغيل اختبار سريع لكل الاستعلامات"""
        print("🎯 بدء اختبار سريع للبحث الحقيقي")
        print(f"📝 سيتم اختبار {len(self.test_queries)} استعلام:")
        print()
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"[{i:2d}/{len(self.test_queries)}]", end=" ")
            await self.test_search_function(query)
            print()
            
            # فترة انتظار قصيرة بين الاختبارات
            await asyncio.sleep(1)
        
        # تحليل النتائج
        successful_searches = sum(1 for r in self.results if r["successful"])
        failed_searches = len(self.results) - successful_searches
        
        if self.search_times:
            avg_time = sum(self.search_times) / len(self.search_times)
            min_time = min(self.search_times)
            max_time = max(self.search_times)
        else:
            avg_time = min_time = max_time = 0
        
        print("="*60)
        print("📊 ملخص نتائج الاختبار السريع:")
        print(f"• إجمالي الاختبارات: {len(self.results)}")
        print(f"• عمليات البحث الناجحة: {successful_searches}")
        print(f"• عمليات البحث الفاشلة: {failed_searches}")
        print(f"• معدل النجاح: {(successful_searches/len(self.results)*100):.1f}%")
        print(f"• متوسط وقت البحث: {avg_time:.3f} ثانية")
        print(f"• أسرع بحث: {min_time:.3f} ثانية")
        print(f"• أبطأ بحث: {max_time:.3f} ثانية")
        
        # تقييم الأداء
        print(f"\n🎯 تقييم الأداء:")
        if avg_time < 0.5:
            print("✅ سرعة البحث ممتازة (أقل من 0.5 ثانية)")
        elif avg_time < 1.0:
            print("✅ سرعة البحث جيدة (0.5-1.0 ثانية)")
        elif avg_time < 2.0:
            print("⚠️ سرعة البحث مقبولة (1.0-2.0 ثانية)")
        else:
            print("❌ سرعة البحث بطيئة (أكثر من 2.0 ثانية)")
        
        if successful_searches / len(self.results) > 0.8:
            print("✅ دقة البحث ممتازة")
        elif successful_searches / len(self.results) > 0.6:
            print("✅ دقة البحث جيدة")
        else:
            print("⚠️ دقة البحث تحتاج تحسين")
        
        # حفظ النتائج
        with open('real_search_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ النتائج في: real_search_test_results.json")
        
        return self.results

async def main():
    """الدالة الرئيسية"""
    tester = RealSearchTester()
    
    try:
        await tester.run_quick_test()
        
        print("\n" + "="*60)
        print("🎯 التوصيات لتحسين أداء النموذج:")
        print("1. إذا كان البحث سريع، فالمشكلة ليست في قاعدة البيانات")
        print("2. تحقق من أوقات استجابة Azure OpenAI")
        print("3. راقب معالجة الصوت والتحويل إلى نص")
        print("4. فحص شبكة الاتصال والـ latency")
        print("5. مراقبة استخدام موارد الخادم")
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل الاختبار: {e}")

if __name__ == "__main__":
    asyncio.run(main())
