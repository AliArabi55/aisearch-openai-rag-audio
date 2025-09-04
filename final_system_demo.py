#!/usr/bin/env python3
"""
اختبار شامل لنظام البحث الدلالي مع الذاكرة المؤقتة
نماذج حقيقية لما سيحدث عندما يستخدم المستخدم Real-time AI
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# إضافة مسار backend للاستيراد
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from ragtools import (
    _search_tool, 
    get_from_cache, 
    save_to_cache, 
    clear_cache,
    SEARCH_CACHE
)

class RealTimeAISimulator:
    """محاكي للذكاء الاصطناعي في الوقت الفعلي"""
    
    def __init__(self):
        """تهيئة المحاكي"""
        load_dotenv("app/backend/.env")
        
        # إعداد البحث
        self.search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.getenv("AZURE_SEARCH_API_KEY")
        self.search_index = os.getenv("AZURE_SEARCH_INDEX")
        self.semantic_config = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
        
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index,
            credential=AzureKeyCredential(self.search_key)
        )
        
        print("🤖 محاكي Real-time AI جاهز!")
        print(f"🔗 الخادم: {self.search_endpoint}")
        print(f"📊 الفهرس: {self.search_index}")
        print(f"🧠 البحث الدلالي: {self.semantic_config}")
        print()
    
    async def user_asks_question(self, user_message: str):
        """محاكاة سؤال المستخدم"""
        print(f"👤 المستخدم: {user_message}")
        print("🤖 AI يفكر...")
        
        # الموديل يقرر أنه يحتاج للبحث
        search_query = self.extract_search_query(user_message)
        print(f"🎯 AI قرر البحث عن: {search_query}")
        
        # تحقق من الذاكرة المؤقتة أولاً
        cached_result = get_from_cache(search_query)
        if cached_result:
            print("🧠 تم العثور على الإجابة في الذاكرة المؤقتة!")
            return self.generate_response_from_cache(cached_result, user_message)
        
        # البحث الدلالي الجديد
        print("🔍 تنفيذ بحث دلالي جديد...")
        search_args = {"query": search_query}
        
        result = await _search_tool(
            search_client=self.search_client,
            semantic_configuration=self.semantic_config,
            identifier_field="ID",
            content_field="ingredients",
            embedding_field="",
            use_vector_query=False,
            args=search_args
        )
        
        # توليد الإجابة
        ai_response = self.generate_ai_response(result.text, user_message)
        print(f"🤖 AI: {ai_response}")
        
        return result.text, ai_response
    
    def extract_search_query(self, user_message: str) -> str:
        """استخراج كلمة البحث من رسالة المستخدم"""
        # منطق بسيط للتوضيح
        user_lower = user_message.lower()
        
        if "بيتزا" in user_lower or "pizza" in user_lower:
            return "pizza"
        elif "برجر" in user_lower or "burger" in user_lower:
            return "burger"
        elif "دجاج" in user_lower or "chicken" in user_lower:
            return "chicken"
        elif "كالزونى" in user_lower or "calzone" in user_lower:
            return "calzone"
        else:
            # استخراج الكلمة الرئيسية
            words = user_message.split()
            for word in words:
                if len(word) > 3:  # كلمات أطول من 3 أحرف
                    return word
            return "food"
    
    def generate_ai_response(self, search_results: str, user_question: str) -> str:
        """توليد إجابة الذكاء الاصطناعي"""
        if "لم أجد" in search_results:
            return "آسف، مش عندي المنتج ده في المطعم"
        
        # استخراج أول منتج من النتائج
        lines = search_results.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('📊') and not line.startswith('🎯'):
                return f"أيوة عندي {line.strip()}. تحب تطلبه؟"
        
        return "عندي أصناف حلوة كتير، تحب إيه بالظبط؟"
    
    def generate_response_from_cache(self, cached_data, user_question: str) -> tuple:
        """توليد إجابة من الذاكرة المؤقتة"""
        if cached_data.get('items'):
            first_item = cached_data['items'][0]
            ai_response = f"من الذاكرة: عندي {first_item['name']} بـ{first_item['price']} جنيه"
            return cached_data.get('response_text', ''), ai_response
        return "بيانات مخزنة", "عندي أصناف حلوة"
    
    async def conversation_simulation(self):
        """محاكاة محادثة كاملة"""
        print("🎭 بدء محاكاة المحادثة...")
        print("=" * 60)
        
        # سيناريو 1: البحث الأول
        print("\n🎬 المشهد الأول: بحث جديد")
        await self.user_asks_question("عايز بيتزا")
        
        print(f"\n🧠 حالة الذاكرة المؤقتة: {len(SEARCH_CACHE)} عنصر محفوظ")
        
        # سيناريو 2: نفس البحث (من الذاكرة)
        print("\n🎬 المشهد الثاني: نفس البحث (من الذاكرة)")
        await self.user_asks_question("إيه أنواع البيتزا اللي عندك؟")
        
        # سيناريو 3: بحث جديد
        print("\n🎬 المشهد الثالث: بحث مختلف")
        await self.user_asks_question("عندك برجر؟")
        
        print(f"\n🧠 حالة الذاكرة المؤقتة: {len(SEARCH_CACHE)} عنصر محفوظ")
        
        # سيناريو 4: مسح الذاكرة (نهاية المكالمة)
        print("\n🎬 المشهد الرابع: نهاية المكالمة")
        clear_cache()
        print("🗑️ تم مسح الذاكرة المؤقتة")
        
        print("\n" + "=" * 60)
        print("✅ انتهت المحاكاة بنجاح!")

def show_system_overview():
    """عرض نظرة عامة على النظام"""
    print("🏗️ نظرة عامة على النظام")
    print("=" * 50)
    print("📞 1. المستخدم يتكلم مع Real-time AI")
    print("🧠 2. AI يحلل الكلام ويقرر البحث")
    print("🔍 3. البحث الدلالي في Azure AI Search")
    print("💾 4. حفظ النتائج في الذاكرة المؤقتة")
    print("🤖 5. AI يرد على المستخدم")
    print("🧠 6. البحثات التالية تستخدم الذاكرة")
    print("🗑️ 7. مسح الذاكرة عند انتهاء المكالمة")
    print()

async def main():
    """الدالة الرئيسية"""
    show_system_overview()
    
    try:
        simulator = RealTimeAISimulator()
        await simulator.conversation_simulation()
    except Exception as e:
        print(f"❌ خطأ في المحاكاة: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
