#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للبحث العربي مع جمل معقدة
"""

import asyncio
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
import sys
import os

# إضافة المجلد الحالي للمسار
sys.path.append(os.path.dirname(__file__))

# استيراد أدوات الترجمة
from translation_utils import translate_arabic_to_english_real

async def test_complex_arabic_queries():
    """اختبار الاستعلامات العربية المعقدة"""
    
    # Azure Search configuration
    endpoint = "https://neslst11mune.search.windows.net"
    index_name = "english1arabic2025-index"
    api_key = "DWfVFVKg1OkGDBAhStHQBGdEAJKn6PLNhh7gP2W4V9AzSeCGfqVN"
    
    credential = AzureKeyCredential(api_key)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    
    # الاستعلامات المعقدة
    complex_queries = [
        "عايز حاجة مع الفراخ مش غالية",
        "اطلب أي حاجة جديدة في المنيو", 
        "هات اكل ايطالي حلو",
        "ايه أرخص ساندوتش عندكم؟",
        "عايز وجبة كاملة مع مشروب",
        "بيتزا كبيرة بكل حاجة عليها",
        "حاجة حارة ومالية"
    ]
    
    print("🔍 اختبار الاستعلامات العربية المعقدة")
    print("=" * 60)
    
    for query in complex_queries:
        print(f"\n🍽️ الاستعلام: '{query}'")
        
        # ترجمة الاستعلام
        translated = translate_arabic_to_english_real(query)
        print(f"🔄 الترجمة: '{translated}'")
        
        # استخراج الكلمات المفتاحية (استخدام الترجمة مباشرة)
        search_query = translated
        print(f"🔍 كلمات البحث: '{search_query}'")
        
        try:
            # البحث في Azure
            async with search_client:
                results = await search_client.search(
                    search_text=search_query,
                    top=3,
                    highlight_fields="name,ingredients"
                )
                
                result_count = 0
                async for result in results:
                    result_count += 1
                    name = result.get('name', 'غير محدد')
                    price = result.get('price', 'غير محدد')
                    print(f"   ✅ {result_count}. {name} - {price} جنيه")
                
                if result_count == 0:
                    print("   ❌ لم توجد نتائج")
        
        except Exception as e:
            print(f"   ❌ خطأ في البحث: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_complex_arabic_queries())
