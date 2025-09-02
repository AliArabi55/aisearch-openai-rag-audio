# قاموس الترجمة من العربية إلى الإنجليزية
ARABIC_TO_ENGLISH = {
    # أطباق رئيسية
    "برجر": "burger",
    "بيتزا": "pizza", 
    "كالزونى": "calzoni",
    "كالزوني": "calzoni",
    "ساندوتش": "sandwich",
    "شوارما": "shawarma",
    
    # أنواع اللحوم
    "فراخ": "ferakh",
    "دجاج": "ferakh",
    "لحمة": "beef",
    "بيف": "beef",
    "لحم": "beef",
    "سلامي": "salami",
    "بسطرمة": "pastirma",
    "باكون": "bacon",
    "هوت دوج": "hot dog",
    
    # الجبن والصوصات
    "جبن": "cheese",
    "جبنة": "cheese",
    "موزاريلا": "mozzarella",
    "شيدر": "cheddar",
    "روكفور": "roquefort",
    "رومي": "romi",
    "كيري": "kiri",
    "مايونيز": "mayonez",
    "صوص": "sauce",
    "صلصة": "salsa",
    "باربكيو": "barbecue",
    "رانش": "ranch",
    "شيلي": "chili",
    
    # الخضروات والإضافات
    "خس": "khas",
    "خيار": "khyar",
    "بصل": "basal",
    "طماطم": "tamata",
    "فلفل": "felfel",
    "زيتون": "zatoon",
    "أناناس": "ananas",
    "مشروم": "mushroom",
    "فطر": "mushroom",
    "هالابينو": "halapeno",
    "حلقات البصل": "onion rings",
    "اونيون رنجز": "onion rings",
    
    # أحجام ووصف
    "كبير": "kbeer",
    "صغير": "sagheer",
    "دبل": "double",
    "سنجل": "single",
    "مشوي": "mashwi",
    "مقلي": "crispy",
    "كريسبي": "crispy",
    "مدخن": "medakhan",
    "مبشور": "mabshour",
    
    # كلمات وصفية
    "لذيذ": "tasty",
    "طعمه حلو": "delicious",
    "حار": "spicy",
    "بارد": "cold",
    "سخن": "hot",
    "طازج": "fresh",
    
    # طلبات شائعة
    "أريد": "I want",
    "عايز": "I want", 
    "بدي": "I want",
    "أطلب": "I order",
    "أحب": "I like",
    "عندك": "do you have",
    "إيه عندك": "what do you have",
    "شوف": "show me",
    "اعرض": "show",
    "بكام": "how much",
    "السعر": "price",
    "كم": "how much",
    "إيه": "what",
    "حاجة": "something",
    "أكلة": "food",
    "طعام": "food",
    
    # كلمات إضافية
    "مع": "with",
    "بدون": "without",
    "إضافة": "add",
    "زيادة": "extra",
    "قليل": "little",
    "كتير": "a lot",
    "شوية": "some",
    "بال": "with",
    "لذيذة": "delicious",
    "لذيذ": "delicious", 
    "بالمشروم": "with mushroom",
    "مشروم": "mushroom",
    "بالباكون": "with bacon",
    "والباكون": "and bacon",
    "باكون": "bacon",
    "بالجبن": "with cheese",
    "والجبن": "and cheese",
    "أمريكان": "american",
    "امريكان": "american",
    "أمريكي": "american",
    "امريكي": "american",
    "دلالي": "semantic",
    "فراخ": "ferakh",
    "دجاج": "ferakh",
    "لحمة": "beef",
    "بيف": "beef",
    "لحم": "beef",
    "سلامي": "salami",
    "بسطرمة": "pastirma",
    "باكون": "bacon",
    "هوت": "hot",
    "دوج": "dog",
    "رانش": "ranch",
    "صوص": "sauce",
    "بالرانش": "with ranch",
    "والرانش": "and ranch"
}

def translate_arabic_to_english(arabic_text):
    """ترجمة النص العربي إلى إنجليزي باستخدام القاموس"""
    import re
    
    # تحويل النص إلى أحرف صغيرة وإزالة علامات الترقيم
    arabic_text = arabic_text.strip().lower()
    
    # البحث عن الكلمات في القاموس
    translated_words = []
    words = re.split(r'\s+', arabic_text)
    
    for word in words:
        # إزالة علامات الترقيم من الكلمة
        clean_word = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', '', word)
        
        if clean_word in ARABIC_TO_ENGLISH:
            translated_words.append(ARABIC_TO_ENGLISH[clean_word])
        elif clean_word:  # إذا لم توجد الكلمة في القاموس، ترجمها بالذكاء الاصطناعي
            # محاولة ترجمة أساسية للكلمات غير الموجودة
            if clean_word:
                translated_words.append(clean_word)  # احتفظ بها مؤقتاً
    
    # دمج الكلمات المترجمة
    translated_text = ' '.join(translated_words)
    
    return translated_text

def extract_food_keywords(translated_text):
    """استخراج كلمات الطعام فقط من النص المترجم للبحث"""
    import re
    
    # كلمات الطعام والمكونات
    food_keywords = [
        # أنواع الطعام
        'burger', 'pizza', 'calzoni', 'sandwich', 'shawarma',
        
        # اللحوم
        'ferakh', 'chicken', 'beef', 'meat', 'salami', 'pastirma', 'bacon', 'hot dog',
        
        # الجبن والصوصات  
        'cheese', 'mozzarella', 'cheddar', 'roquefort', 'sauce', 'ranch', 'barbecue', 'chili',
        
        # الخضروات والإضافات
        'mushroom', 'onion', 'tomato', 'lettuce', 'pickle', 'rings', 'ananas', 'pineapple',
        
        # أوصاف الطعام
        'crispy', 'double', 'single', 'american', 'spicy', 'tasty', 'delicious', 'juicy',
        'cheesy', 'vibes', 'crazy', 'delight', 'special',
        
        # أحجام
        'kbeer', 'large', 'small', 'wost', 'medium'
    ]
    
    # استخراج كلمات الطعام من النص
    words = translated_text.lower().split()
    food_words = []
    
    for word in words:
        # إزالة علامات الترقيم
        clean_word = re.sub(r'[^\w]', '', word)
        if clean_word in food_keywords:
            food_words.append(clean_word)
    
    # إرجاع النص للبحث (كلمات الطعام فقط)
    return ' '.join(food_words) if food_words else translated_text

def translate_and_extract_for_search(arabic_text):
    """ترجمة كاملة + استخراج كلمات الطعام للبحث"""
    
    # الترجمة الكاملة
    full_translation = translate_arabic_to_english(arabic_text)
    
    # استخراج كلمات الطعام للبحث
    search_query = extract_food_keywords(full_translation)
    
    return {
        'original': arabic_text,
        'full_translation': full_translation,
        'search_query': search_query
    }

def search_with_translation(query):
    """ترجمة الاستعلام ثم البحث"""
    # ترجمة الاستعلام
    english_query = translate_arabic_to_english(query)
    
    print(f"🔄 الاستعلام الأصلي: {query}")
    print(f"🔄 الاستعلام المترجم: {english_query}")
    
    return english_query

if __name__ == "__main__":
    # اختبار النظام الجديد
    test_queries = [
        "أريد برجر بالجبن",
        "عايز بيتزا فراخ", 
        "بدي كالزوني لحمة",
        "إيه عندك برجر كريسبي",
        "أطلب ساندوتش دجاج مشوي مع جبنة شيدر",
        "عايز حاجة لذيذة بالمشروم والباكون",
        "عايز حاجة أمريكان",
        "أطلب حاجة بالرانش صوص"
    ]
    
    print("🧪 اختبار النظام الجديد للترجمة والاستخراج:")
    print("=" * 70)
    
    for query in test_queries:
        result = translate_and_extract_for_search(query)
        print(f"العربي: {result['original']}")
        print(f"الترجمة الكاملة: {result['full_translation']}")
        print(f"كلمات البحث: {result['search_query']}")
        print("-" * 50)
