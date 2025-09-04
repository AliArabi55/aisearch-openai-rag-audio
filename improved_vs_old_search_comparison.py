#!/usr/bin/env python3
"""
improved_vs_old_search_comparison.py
🆚 مقارنة البحث المحسن مع البحث القديم
"""

import asyncio
import os
import sys
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# تحميل متغيرات البيئة من مجلد app/backend
env_path = os.path.join(os.path.dirname(__file__), "app", "backend", ".env")
load_dotenv(env_path)

async def compare_search_methods():
    """
    🆚 مقارنة طرق البحث المختلفة
    """
    print("🆚 مقارنة البحث المحسن مع البحث القديم")
    print("=" * 70)
    
    # إعداد Azure Search
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    semantic_config = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # عينات للمقارنة
    test_samples = [
        "Chicken Pizza",
        "Double Burger", 
        "BBQ",
        "Large Seafood",
        "Ranch"
    ]
    
    for sample in test_samples:
        print(f"\n🔍 البحث عن: '{sample}'")
        print("=" * 50)
        
        # البحث القديم (ingredients فقط)
        print("📊 البحث القديم (ingredients فقط):")
        try:
            old_results = search_client.search(
                search_text=sample,
                query_type="semantic",
                semantic_configuration_name=semantic_config,
                top=3,
                select="ID,Name,ingredients,Price",
                search_fields=["ingredients"],  # ingredients فقط
                query_caption="extractive",
                query_answer="extractive"
            )
            
            old_count = 0
            old_scores = []
            for result in old_results:
                old_count += 1
                semantic_score = result.get("@search.reranker_score", 0)
                old_scores.append(semantic_score)
                print(f"   {old_count}. {result.get('Name', '')} - {semantic_score:.2f}")
            
            print(f"   📊 عدد النتائج: {old_count}")
            if old_scores:
                print(f"   📈 متوسط النقاط: {sum(old_scores)/len(old_scores):.2f}")
        except Exception as e:
            print(f"   ❌ خطأ: {str(e)}")
            old_count = 0
            old_scores = []
        
        print()
        
        # البحث المحسن (Name + ingredients)
        print("🚀 البحث المحسن (Name + ingredients):")
        try:
            new_results = search_client.search(
                search_text=sample,
                query_type="semantic",
                semantic_configuration_name=semantic_config,
                top=3,
                select="ID,Name,ingredients,Price",
                search_fields=["Name", "ingredients"],  # Name + ingredients
                query_caption="extractive",
                query_answer="extractive"
            )
            
            new_count = 0
            new_scores = []
            for result in new_results:
                new_count += 1
                semantic_score = result.get("@search.reranker_score", 0)
                new_scores.append(semantic_score)
                print(f"   {new_count}. {result.get('Name', '')} - {semantic_score:.2f}")
            
            print(f"   📊 عدد النتائج: {new_count}")
            if new_scores:
                print(f"   📈 متوسط النقاط: {sum(new_scores)/len(new_scores):.2f}")
        except Exception as e:
            print(f"   ❌ خطأ: {str(e)}")
            new_count = 0
            new_scores = []
        
        # تحليل التحسن
        print()
        print("📊 تحليل التحسن:")
        improvement = new_count - old_count
        if improvement > 0:
            print(f"   ✅ تحسن: +{improvement} نتائج إضافية")
        elif improvement < 0:
            print(f"   ⚠️ تراجع: {improvement} نتائج أقل")
        else:
            print(f"   ➖ نفس العدد من النتائج")
        
        if old_scores and new_scores:
            score_improvement = (sum(new_scores)/len(new_scores)) - (sum(old_scores)/len(old_scores))
            if score_improvement > 0:
                print(f"   ✅ تحسن النقاط: +{score_improvement:.2f}")
            else:
                print(f"   ➖ النقاط: {score_improvement:.2f}")
        
        print("-" * 50)
    
    print("\n✅ اكتملت المقارنة!")

if __name__ == "__main__":
    asyncio.run(compare_search_methods())
