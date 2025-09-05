"""
إعدادات الموديل لتحديد كيفية عرض النتائج
"""

class ModelInputSettings:
    _current_mode = "name_and_price"  # default mode
    _ingredients_enabled = True  # المكونات مفعلة افتراضياً
    
    @classmethod
    def get_current_mode(cls):
        """الحصول على الوضع الحالي"""
        if cls._ingredients_enabled:
            return "الاسم والسعر والمكونات"
        else:
            return "الاسم والسعر فقط"
    
    @classmethod
    def get_display_config(cls):
        """الحصول على إعدادات العرض"""
        return {
            "ingredients_enabled": cls._ingredients_enabled,
            "mode": cls._current_mode
        }
    
    @classmethod
    def set_name_and_price_only(cls):
        """تعيين عرض الاسم والسعر فقط"""
        cls._current_mode = "name_and_price"
        cls._ingredients_enabled = False
        return "تم تعيين عرض الاسم والسعر فقط"
    
    @classmethod
    def enable_ingredients(cls):
        """تفعيل عرض المكونات"""
        cls._ingredients_enabled = True
        cls._current_mode = "name_price_ingredients"
        return "تم تفعيل عرض المكونات"
    
    @classmethod
    def disable_ingredients(cls):
        """إلغاء تفعيل عرض المكونات"""
        cls._ingredients_enabled = False
        cls._current_mode = "name_and_price"
        return "تم إلغاء تفعيل عرض المكونات"
    
    @classmethod
    def toggle_ingredients(cls):
        """تبديل حالة عرض المكونات"""
        cls._ingredients_enabled = not cls._ingredients_enabled
        if cls._ingredients_enabled:
            cls._current_mode = "name_price_ingredients"
            return "تم تفعيل عرض المكونات"
        else:
            cls._current_mode = "name_and_price"
            return "تم إلغاء تفعيل عرض المكونات"
    
    @classmethod
    def set_full_details(cls):
        """تعيين عرض جميع التفاصيل"""
        cls._ingredients_enabled = True
        cls._current_mode = "full_details"
        return "تم تعيين عرض جميع التفاصيل"


def generate_model_input(docs, query, search_query):
    """
    توليد النص المبسط الذي سيتم إرساله للموديل
    التنسيق: رقم- الاسم، السعر
    """
    if not docs:
        return "لم يتم العثور على نتائج مطابقة لبحثك."
    
    # بناء قائمة مبسطة
    result_parts = []
    
    for i, doc in enumerate(docs, 1):
        name = doc.get('Name', 'غير محدد')
        price = doc.get('Price', 'غير محدد')
        
        # تحسين التحقق من السعر - معالجة الأرقام والنصوص
        price_available = (
            price is not None and 
            str(price).strip() and 
            str(price) != "غير محدد" and
            str(price) != "None" and
            str(price) != ""
        )
        
        # تنسيق مبسط: Name: [name], Price: [price]
        if price_available:
            result_parts.append(f"Name: {name}, Price: {price}")
        else:
            result_parts.append(f"Name: {name}, Price: غير متاح")
            
        # طباعة تشخيصية للمطورين
        print(f"🔍 العنصر {i}: {name}")
        print(f"   💰 السعر الخام: {price} (نوع: {type(price)})")
        print(f"   ✅ السعر متاح: {price_available}")
    
    return "\n".join(result_parts)
