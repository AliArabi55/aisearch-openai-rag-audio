#!/usr/bin/env python3
import asyncio
import json
import os
import sys
from datetime import datetime

# إضافة مجلد backend للمسار
sys.path.append('app/backend')

async def simple_onion_rings_direct_test():
    """اختبار مباشر لأونين رينجز عبر الاستيراد من التطبيق الأساسي"""
    
    print("🧅 اختبار مباشر لأونين رينجز")
    print("=" * 50)
    
    try:
        # قراءة الإعدادات من app.py
        print("📖 قراءة الإعدادات من التطبيق...")
        
        # قراءة ملف .env مباشرة
        env_file = 'app/backend/.env'
        config = {}
        
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"\'')
        
        search_endpoint = config.get('AZURE_SEARCH_ENDPOINT')
        search_key = config.get('AZURE_SEARCH_ADMIN_KEY')
        search_index = config.get('AZURE_SEARCH_INDEX')
        semantic_config = config.get('AZURE_SEARCH_SEMANTIC_CONFIGURATION')
        
        print(f"🔧 الإعدادات المقروءة:")
        print(f"   المؤشر: {search_index}")
        print(f"   التكوين الدلالي: {semantic_config}")
        print(f"   نقطة النهاية: {search_endpoint[:50] if search_endpoint else 'غير محدد'}...")
        
        if not all([search_endpoint, search_key, search_index, semantic_config]):
            print("❌ بعض الإعدادات مفقودة")
            return
            
    except Exception as e:
        print(f"❌ خطأ في قراءة الإعدادات: {e}")
        return
    
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        from translation_utils import translate_arabic_to_english
        
        # إنشاء عميل البحث
        credentials = AzureKeyCredential(search_key)
        search_client = SearchClient(search_endpoint, search_index, credentials)
        print("✅ تم إنشاء عميل البحث بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء عميل البحث: {e}")
        return
    
    # اختبارات البحث
    search_tests = [
        "أونين رينجز",
        "onion rings", 
        "حلقات البصل",
        "rings",
        "بصل"
    ]
    
    print(f"\n🔍 سأختبر {len(search_tests)} بحث:")
    
    all_results = []
    
    for i, search_term in enumerate(search_tests, 1):
        print(f"\n🧪 اختبار {i}: '{search_term}'")
        
        try:
            # ترجمة إذا كان عربي
            if any(ord(char) > 127 for char in search_term):  # نص عربي
                translated = translate_arabic_to_english(search_term)
                print(f"   📝 الترجمة: '{search_term}' → '{translated}'")
                search_query = translated
            else:
                search_query = search_term
                print(f"   📝 البحث المباشر: '{search_term}'")
            
            # البحث الدلالي
            try:
                results = search_client.search(
                    search_text=search_query,
                    search_fields=["Name", "ingredients"],
                    select=["ID", "Name", "ingredients"],
                    query_type="semantic",
                    semantic_configuration_name=semantic_config,
                    top=3
                )
                
                found_items = []
                for doc in results:
                    item_name = doc.get('Name', 'بدون اسم')
                    item_ingredients = doc.get('ingredients', 'بدون مكونات')
                    
                    print(f"   📄 {item_name}")
                    print(f"      المكونات: {item_ingredients[:80]}...")
                    
                    # فحص إذا كان هذا أونين رينجز
                    is_onion_rings = (
                        'onion' in item_name.lower() or 
                        'onion' in item_ingredients.lower() or
                        'ring' in item_name.lower() or
                        'ring' in item_ingredients.lower() or
                        'بصل' in item_name or 
                        'بصل' in item_ingredients
                    )
                    
                    found_items.append({
                        'name': item_name,
                        'ingredients': item_ingredients,
                        'is_likely_onion_rings': is_onion_rings,
                        'id': doc.get('ID')
                    })
                
                print(f"   ✅ تم العثور على {len(found_items)} عنصر")
                
                # فحص وجود أونين رينجز
                onion_rings_items = [item for item in found_items if item['is_likely_onion_rings']]
                if onion_rings_items:
                    print(f"   🧅 يحتوي على أونين رينجز محتمل: {len(onion_rings_items)} عنصر")
                    for or_item in onion_rings_items:
                        print(f"      ➤ {or_item['name']}")
                else:
                    print(f"   ❌ لا يحتوي على أونين رينجز")
                
                all_results.append({
                    'search_term': search_term,
                    'translated_term': search_query,
                    'total_found': len(found_items),
                    'onion_rings_found': len(onion_rings_items),
                    'items': found_items
                })
                
            except Exception as e:
                print(f"   💥 خطأ في البحث: {e}")
                all_results.append({
                    'search_term': search_term,
                    'error': str(e)
                })
            
        except Exception as e:
            print(f"   💥 خطأ في الترجمة أو المعالجة: {e}")
        
        # انتظار قصير
        await asyncio.sleep(0.3)
    
    # ملخص النتائج
    print("\n" + "=" * 50)
    print("📊 ملخص النتائج:")
    print("=" * 50)
    
    successful_tests = [r for r in all_results if 'total_found' in r and r['total_found'] > 0]
    onion_rings_tests = [r for r in all_results if 'onion_rings_found' in r and r['onion_rings_found'] > 0]
    
    print(f"📈 نتائج البحث:")
    print(f"   🔍 عمليات بحث ناجحة: {len(successful_tests)}/{len(search_tests)}")
    print(f"   🧅 عمليات عثور على أونين رينجز: {len(onion_rings_tests)}")
    
    if onion_rings_tests:
        print(f"\n🧅 أونين رينجز الموجود:")
        for test in onion_rings_tests:
            print(f"   ✅ البحث: '{test['search_term']}' - {test['onion_rings_found']} عنصر")
            for item in test['items']:
                if item['is_likely_onion_rings']:
                    print(f"      ➤ {item['name']} (ID: {item['id']})")
    else:
        print(f"\n❌ لم يتم العثور على أونين رينجز في أي بحث")
    
    # حفظ التقرير
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"onion_rings_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'config': {
                'search_index': search_index,
                'semantic_config': semantic_config
            },
            'summary': {
                'total_tests': len(search_tests),
                'successful_tests': len(successful_tests),
                'onion_rings_found_tests': len(onion_rings_tests)
            },
            'all_results': all_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 تم حفظ التقرير في: {report_file}")
    
    # تشخيص المشكلة
    print(f"\n🔍 تشخيص المشكلة:")
    if len(onion_rings_tests) == 0:
        print("   ❌ لم يتم العثور على أونين رينجز مطلقاً")
        print("   💡 الأسباب المحتملة:")
        print("      - البيانات غير موجودة في الفهرس")
        print("      - مشكلة في الترجمة")
        print("      - مشكلة في البحث الدلالي")
    elif len(onion_rings_tests) < len(search_tests):
        print("   ⚠️  نتائج غير متسقة - أحياناً يجد وأحياناً لا يجد")
        print("   💡 السبب المحتمل: مشكلة في الترجمة أو حساسية البحث")
    else:
        print("   ✅ النتائج متسقة - يجد أونين رينجز دائماً")

if __name__ == "__main__":
    asyncio.run(simple_onion_rings_direct_test())
