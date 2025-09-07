#!/usr/bin/env python3
"""
اختبار البحث الاستدلالي لجملة "اريد بيتزا تونه وسط"
"""
import asyncio
import os
import sys
from pathlib import Path

# إضافة مسار التطبيق للـ sys.path
app_backend_path = Path(__file__).parent / "app" / "backend"
sys.path.append(str(app_backend_path))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from translation_utils import translate_and_extract_for_search

# تحديد ترميز الخرج للعربية في الويندوز
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

async def test_search():
    """اختبار البحث الاستدلالي"""
    
    # تحميل متغيرات البيئة
    load_dotenv()
    
    # إعدادات البحث
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX_NAME")  # تصحيح اسم المتغير
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    semantic_configuration = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    # إنشاء عميل البحث
    if search_key:
        search_credential = AzureKeyCredential(search_key)
    else:
        search_credential = DefaultAzureCredential()
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=search_credential
    )
    
    # النص المطلوب البحث عنه
    original_query = "اريد بيتزا تونه وسط"
    
    print("="*60)
    print("🔍 اختبار البحث الاستدلالي")
    print("="*60)
    print(f"📝 النص الأصلي: {original_query}")
    
    # ترجمة النص
    translated_query, mode = translate_and_extract_for_search(original_query)
    print(f"🌐 النص المترجم: {translated_query}")
    print(f"🔧 وضع الترجمة: {mode}")
    print()
    
    # تنفيذ البحث الاستدلالي
    print("🎯 تنفيذ البحث الاستدلالي...")
    try:
        if semantic_configuration:
            search_results = search_client.search(
                search_text=translated_query,
                query_type="semantic", 
                semantic_configuration_name=semantic_configuration,
                top=5,
                select="ID,Name,ingredients,Price",
                search_fields=["Name", "ingredients"],
                query_caption="extractive",
                query_answer="extractive"
            )
            search_type = "semantic (استدلالي)"
        else:
            search_results = search_client.search(
                search_text=translated_query,
                query_type="simple",
                top=5,
                select="ID,Name,ingredients,Price",
                search_fields=["Name", "ingredients"]
            )
            search_type = "simple (بسيط)"
        
        print(f"✅ نوع البحث: {search_type}")
        print()
        
        # عرض النتائج
        print("📊 نتائج البحث:")
        print("-" * 60)
        
        results_list = list(search_results)
        if not results_list:
            print("❌ لم يتم العثور على نتائج")
            return
            
        print(f"📈 عدد النتائج: {len(results_list)}")
        print()
        
        for i, result in enumerate(results_list, 1):
            name = result.get("Name", "غير محدد")
            price = result.get("Price", "غير محدد")
            ingredients = result.get("ingredients", "غير محدد")
            search_score = result.get("@search.score", 0)
            semantic_score = result.get("@search.reranker_score", "غير متاح")
            
            print(f"🍕 النتيجة {i}:")
            print(f"   📛 الاسم: {name}")
            print(f"   💰 السعر: {price}")
            print(f"   🥘 المكونات: {ingredients[:100]}{'...' if len(str(ingredients)) > 100 else ''}")
            print(f"   📊 درجة البحث: {search_score:.3f}")
            if semantic_score != "غير متاح":
                print(f"   🎯 درجة الاستدلال: {semantic_score:.3f}")
            print()
        
        # تحليل نوع البيانات للأسعار
        print("🔍 تحليل أنواع البيانات للأسعار:")
        print("-" * 40)
        for i, result in enumerate(results_list, 1):
            name = result.get("Name", "غير محدد")
            price = result.get("Price", "غير محدد")
            price_type = type(price).__name__
            print(f"   {i}. {name}: Price={price} (نوع: {price_type})")
        
        print()
        print("="*60)
        print("✅ انتهى الاختبار بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في البحث: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())
