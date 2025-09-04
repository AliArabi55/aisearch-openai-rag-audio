#!/usr/bin/env python3
import asyncio
import json
import os
import sys
from datetime import datetime

# إضافة مجلد backend للمسار
sys.path.append('app/backend')

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from translation_utils import translate_arabic_to_english as translate_to_english

async def test_onion_rings_search():
    """اختبار مبسط لمشكلة أونين رينجز باستخدام نفس الإعدادات"""
    
    print("🧅 اختبار مشكلة أونين رينجز - إصدار مبسط")
    print("=" * 60)
    
    # قراءة الإعدادات من ملف .env
    try:
        from dotenv import load_dotenv
        load_dotenv('app/backend/.env')
        
        search_endpoint = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')
        search_key = os.getenv('AZURE_SEARCH_ADMIN_KEY')
        search_index = os.getenv('AZURE_SEARCH_INDEX')
        semantic_config = os.getenv('AZURE_SEARCH_SEMANTIC_CONFIGURATION')
        
        print(f"🔧 إعدادات البحث:")
        print(f"   المؤشر: {search_index}")
        print(f"   التكوين الدلالي: {semantic_config}")
        print(f"   نقطة النهاية: {search_endpoint}")
        
    except Exception as e:
        print(f"❌ خطأ في قراءة الإعدادات: {e}")
        return
    
    # إنشاء عميل البحث
    try:
        credentials = AzureKeyCredential(search_key)
        search_client = SearchClient(search_endpoint, search_index, credentials)
        print("✅ تم إنشاء عميل البحث بنجاح")
    except Exception as e:
        print(f"❌ خطأ في إنشاء عميل البحث: {e}")
        return
    
    # قائمة تغيرات البحث
    search_variations = [
        "أونين رينجز",
        "اونين رينجز", 
        "أونيان رينجز",
        "حلقات البصل",
        "onion rings",
        "Onion Rings",
        "rings",
        "بصل مقلي"
    ]
    
    print(f"\n🔍 سأختبر {len(search_variations)} طريقة بحث:")
    
    results = []
    
    for i, search_term in enumerate(search_variations, 1):
        print(f"\n🧪 اختبار {i}: '{search_term}'")
        
        try:
            # ترجمة النص
            translated_term = translate_to_english(search_term)
            print(f"   📝 الترجمة: '{search_term}' → '{translated_term}'")
            
            # إعداد استعلام البحث الدلالي
            search_query = {
                "search_text": translated_term,
                "search_fields": ["Name", "ingredients"],
                "select": ["ID", "Name", "ingredients"],
                "query_type": "semantic",
                "semantic_configuration_name": semantic_config,
                "query_caption": "extractive",
                "query_answer": "extractive",
                "top": 5
            }
            
            # تنفيذ البحث
            search_result = search_client.search(**search_query)
            
            # تحليل النتائج
            items_found = []
            for doc in search_result:
                print(f"   📄 نتيجة: {doc.get('Name', 'بدون اسم')}")
                print(f"       المكونات: {doc.get('ingredients', 'بدون مكونات')[:100]}...")
                items_found.append({
                    'id': doc.get('ID'),
                    'name': doc.get('Name'), 
                    'ingredients': doc.get('ingredients')
                })
            
            if items_found:
                print(f"   ✅ تم العثور على {len(items_found)} عنصر")
            else:
                print(f"   ❌ لم يتم العثور على أي نتائج")
            
            results.append({
                'search_term': search_term,
                'translated_term': translated_term,
                'items_found': len(items_found),
                'results': items_found[:2]  # أول نتيجتين فقط
            })
            
        except Exception as e:
            print(f"   💥 خطأ في البحث: {e}")
            results.append({
                'search_term': search_term,
                'translated_term': translated_term,
                'items_found': 0,
                'error': str(e)
            })
        
        # انتظار قصير
        await asyncio.sleep(0.5)
    
    # ملخص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج:")
    print("=" * 60)
    
    successful_searches = [r for r in results if r['items_found'] > 0]
    print(f"📈 عمليات بحث ناجحة: {len(successful_searches)}/{len(results)}")
    
    print(f"\n📋 تفاصيل النتائج:")
    for i, result in enumerate(results, 1):
        status = f"✅ {result['items_found']} نتيجة" if result['items_found'] > 0 else "❌ لا توجد نتائج"
        print(f"   {i:2d}. '{result['search_term']}' → {status}")
    
    # البحث عن أونين رينجز تحديداً في النتائج
    onion_rings_found = []
    for result in successful_searches:
        for item in result.get('results', []):
            name = item.get('name', '').lower()
            ingredients = item.get('ingredients', '').lower()
            if 'onion' in name or 'onion' in ingredients or 'بصل' in name or 'بصل' in ingredients:
                onion_rings_found.append({
                    'search_term': result['search_term'],
                    'item': item
                })
    
    if onion_rings_found:
        print(f"\n🧅 أونين رينجز الموجود:")
        for item in onion_rings_found:
            print(f"   📍 البحث: '{item['search_term']}'")
            print(f"      الاسم: {item['item'].get('name')}")
            print(f"      المكونات: {item['item'].get('ingredients', '')[:100]}...")
    else:
        print(f"\n❌ لم يتم العثور على أونين رينجز في أي من النتائج")
    
    # حفظ النتائج
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"onion_rings_test_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'summary': {
                'total_searches': len(results),
                'successful_searches': len(successful_searches),
                'onion_rings_found': len(onion_rings_found)
            },
            'detailed_results': results,
            'onion_rings_items': onion_rings_found
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 تم حفظ التقرير في: {filename}")

if __name__ == "__main__":
    asyncio.run(test_onion_rings_search())
