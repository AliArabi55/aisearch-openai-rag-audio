"""
اختبار البحث الدلالي لجملة "انا اريد بيتزا تونة وسط"
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ragtools import semantic_search_with_cache

# تشغيل البحث
search_query = "انا اريد بيتزا تونة وسط"
print(f"🔍 البحث عن: {search_query}")

# تنفيذ البحث
results = semantic_search_with_cache(
    search_query=search_query,
    search_client=None,  # سيتم إنشاؤه داخلياً
    search_index="english22-index",
    semantic_configuration="english22 semantic configuration",
    identifier_field="ID",
    content_field="ingredients",
    title_field="Name"
)

print("\n📋 النتائج:")
if results and 'docs' in results:
    for i, doc in enumerate(results['docs'], 1):
        print(f"\n{i}. 📝 الاسم: {doc.get('Name', 'غير متوفر')}")
        if 'Price' in doc:
            print(f"   💰 السعر: {doc['Price']}")
        if 'ingredients' in doc:
            print(f"   🥗 المكونات: {doc['ingredients']}")
        print(f"   🔢 ID: {doc.get('ID', 'غير متوفر')}")
else:
    print("❌ لم يتم العثور على نتائج")
