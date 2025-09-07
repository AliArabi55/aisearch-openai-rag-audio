#!/usr/bin/env python3
"""
اختبار تدفق البيانات إلى الموديل الحقيقي
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
from model_input_settings import ModelInputSettings, generate_model_input

# تحديد ترميز الخرج للعربية في الويندوز
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

async def test_model_input():
    """اختبار ما يذهب للموديل"""
    
    # تحميل متغيرات البيئة
    load_dotenv()
    
    # إعدادات البحث
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX_NAME")
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
    
    print("="*70)
    print("🎯 اختبار تدفق البيانات إلى الموديل Real-time")
    print("="*70)
    print(f"📝 السؤال الأصلي: {original_query}")
    
    # ترجمة النص
    translated_query, mode = translate_and_extract_for_search(original_query)
    print(f"🌐 النص المترجم: {translated_query}")
    print()
    
    # تنفيذ البحث
    try:
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
        
        # تحويل النتائج إلى قائمة
        docs = []
        for r in search_results:
            docs.append({
                'ID': r.get("ID", "غير محدد"),
                'Name': r.get("Name", "غير محدد"),
                'ingredients': r.get("ingredients", "غير محدد"),
                'Price': r.get("Price", "غير محدد"),
                'search_score': r.get("@search.score", 0),
                'semantic_score': r.get("@search.reranker_score", None)
            })
        
        print("📊 نتائج البحث الخام:")
        print("-" * 50)
        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc['Name']} - السعر: {doc['Price']} - النوع: {type(doc['Price'])}")
        
        print()
        print("🎛️ إعدادات الموديل الحالية:")
        print(f"   {ModelInputSettings.get_current_mode()}")
        print()
        
        # تنسيق البيانات للموديل
        model_input = generate_model_input(docs, original_query, translated_query)
        
        print("📤 البيانات التي ستُرسل لموديل gpt-4o-realtime-preview:")
        print("="*70)
        print(model_input)
        print("="*70)
        
        print(f"📏 حجم النص: {len(model_input)} حرف")
        print(f"📊 عدد العناصر: {len(docs)}")
        
        # تحليل مشكلة الأسعار
        print()
        print("🔍 تحليل مشكلة الأسعار:")
        print("-" * 40)
        
        for i, doc in enumerate(docs, 1):
            price = doc['Price']
            price_type = type(price).__name__
            
            # التحقق من توفر السعر حسب منطق الكود
            price_available = (
                price is not None and 
                str(price).strip() and 
                str(price) != "غير محدد" and
                str(price) != "None" and
                str(price) != ""
            )
            
            print(f"   {i}. {doc['Name']}")
            print(f"      السعر الخام: {price} (نوع: {price_type})")
            print(f"      متاح؟ {price_available}")
            
            if price_available:
                print(f"      ✅ سيظهر في الموديل: Price: {price}")
            else:
                print(f"      ❌ سيظهر في الموديل: Price: غير متاح")
            print()
        
    except Exception as e:
        print(f"❌ خطأ في البحث: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_model_input())
