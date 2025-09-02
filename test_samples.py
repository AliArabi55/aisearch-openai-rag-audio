import asyncio
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from translation_utils import translate_and_extract_for_search

# تحميل متغيرات البيئة
load_dotenv(dotenv_path="./app/backend/.env")

async def test_semantic_search_samples():
    """اختبار البحث الدلالي على العينات المطلوبة"""
    
    # إعداد العميل
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")  
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    semantic_config = "334455"  # التكوين الدلالي المطلوب
    
    print("🧪 اختبار البحث الدلالي على العينات المحددة")
    print("=" * 60)
    print(f"🔍 معلومات الاتصال:")
    print(f"   النقطة: {search_endpoint}")
    print(f"   الفهرس: {search_index}")
    print(f"   التكوين الدلالي: {semantic_config}")
    print()
    
    # إنشاء العميل
    credential = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, search_index, credential)
    
    # العينات المطلوب اختبارها
    print("📋 العينات المتوقعة في الفهرس:")
    expected_samples = [
        {"ID": 1, "Name": "Calzoni Ferakh Crispy Kbeer", "Price": 180, "Ingredients": "Salsa - Felfel - Zatoon - Mozzarella - Ferakh Crispy"},
        {"ID": 2, "Name": "Calzoni Ferakh Barbecue Kbeer", "Price": 180, "Ingredients": "Salsa - Felfel - Zatoon - Mozzarella - Ferakh - Sauce Barbecue"},
        {"ID": 4, "Name": "Cheesy Crispy Double", "Price": 220, "Ingredients": "Mayonez - Khas - Khyar Mekhalel - Basal - Sauce Circles - Roquefort - Gebn Romi - Kiri Sauce - Cheddar Sauce"},
        {"ID": 5, "Name": "American Crispy Double", "Price": 210, "Ingredients": "Mayonez - Khas - Khyar Mekhalel - Basal - Sauce Circles - Hot Dog - Onion Rings - Beef Chili Sauce - Cheddar Sauce"},
        {"ID": 6, "Name": "Vibes Crispy Double", "Price": 230, "Ingredients": "Mayonez - Khas - Khyar Mekhalel - Basal - Sauce Circles - Sharayeh Ananas - Cheddar Sauce - Romi Medakhan - Ranch Sauce"},
        {"ID": 7, "Name": "Crazy Ranch Crispy Double", "Price": 250, "Ingredients": "Mayonez - Khas - Khyar Mekhalel - Basal - Sauce Circles - Halapeno - Mushroom - Chili Sauce - Ranch Sauce"},
        {"ID": 8, "Name": "Juicy Crispy Double", "Price": 230, "Ingredients": "Mayonez - Khas - Khyar Mekhalel - Basal - Sauce Circles - Dajaj Mashwi - Crispy - Mushroom - Bacon - Cheddar Sauce"},
        {"ID": 9, "Name": "Delight Crispy Double", "Price": 230, "Ingredients": "Mayonez - Khas - Khyar Mekhalel - Basal - Sauce Circles - Salami - Pastirma - Romi Mabshour - Sauce Cheddar"},
        {"ID": 10, "Name": "Tasty Crispy Double", "Price": 220, "Ingredients": "Mayonez - Khas - Khyar Mekhalel - Basal - Sauce Circles - Onion Rings - Mozzarella Sticks - Romi Medakhan - Salami"}
    ]
    
    for sample in expected_samples[:5]:  # عرض أول 5 عينات
        print(f"   {sample['ID']}. {sample['Name']} - {sample['Price']} جنيه")
    print("   ...")
    print()
    
    # استعلامات الاختبار
    test_scenarios = [
        {
            "arabic": "أريد برجر كريسبي بالجبن",
            "description": "البحث عن برجر كريسبي بالجبن"
        },
        {
            "arabic": "عايز حاجة أمريكان",
            "description": "البحث عن أطعمة أمريكية"
        },
        {
            "arabic": "بدي أكلة بالمشروم والباكون",
            "description": "البحث عن أطعمة بالمشروم والباكون"
        },
        {
            "arabic": "شوف لي كالزوني فراخ",
            "description": "البحث عن كالزوني فراخ"
        },
        {
            "arabic": "أطلب حاجة بالرانش صوص",
            "description": "البحث عن أطعمة بصوص الرانش"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🔍 سيناريو {i}: {scenario['description']}")
        print(f"👤 العميل يقول: '{scenario['arabic']}'")
        print("-" * 50)
        
        # ترجمة الاستعلام والاستخراج
        translation_result = translate_and_extract_for_search(scenario['arabic'])
        print(f"🔄 الترجمة الكاملة: '{translation_result['full_translation']}'")
        print(f"🎯 كلمات البحث: '{translation_result['search_query']}'")
        
        # استخدام كلمات البحث للبحث الدلالي
        search_query = translation_result['search_query']
        
        try:
            # البحث الدلالي
            search_results = await search_client.search(
                search_text=search_query,
                query_type="semantic",
                semantic_configuration_name=semantic_config,
                top=3,
                query_caption="extractive",
                query_answer="extractive"
            )
            
            print(f"\n📊 نتائج البحث الدلالي:")
            
            found_items = []
            async for result in search_results:
                name = result.get('Name', 'بدون اسم')
                price = result.get('Price', 'غير محدد')
                reranker_score = result.get('@search.reranker_score', 0)
                ingredients = result.get('ingredients', '')
                item_id = result.get('ID', '')
                
                found_items.append({
                    'ID': item_id,
                    'Name': name,
                    'Price': price,
                    'Score': reranker_score,
                    'Ingredients': ingredients
                })
            
            if found_items:
                print(f"🎯 عُثر على {len(found_items)} نتيجة:")
                for j, item in enumerate(found_items, 1):
                    print(f"   {j}. {item['Name']}")
                    print(f"      💰 السعر: {item['Price']} جنيه")
                    print(f"      🎯 الدرجة الدلالية: {item['Score']:.3f}")
                    print(f"      🥘 المكونات: {item['Ingredients'][:70]}...")
                    print()
                
                # ما سيراه الموديل
                best_match = found_items[0]
                print(f"🤖 ما سيحصل عليه الموديل:")
                print(f"   Name: {best_match['Name']}")
                print(f"   Price: {best_match['Price']}")
                print(f"   (هذا ما سيستخدمه الموديل لتكوين الرد)")
                
            else:
                print("   ❌ لم يجد نتائج")
                
        except Exception as e:
            print(f"❌ خطأ في البحث: {e}")
        
        print("\n" + "=" * 60)
        print()
    
    await search_client.close()
    
    print("🎉 انتهى اختبار البحث الدلالي!")
    print("✅ النظام جاهز للاستخدام مع البحث الدلالي والترجمة")

if __name__ == "__main__":
    asyncio.run(test_semantic_search_samples())
