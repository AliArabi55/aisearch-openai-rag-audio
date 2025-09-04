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
    توليد النص الذي سيتم إرساله للموديل
    """
    if not docs:
        return "لم يتم العثور على نتائج مطابقة لبحثك."
    
    config = ModelInputSettings.get_display_config()
    
    # بناء النص بناءً على الإعدادات
    result_parts = []
    
    for doc in docs:
        item_parts = []
        
        # الاسم دائماً موجود
        if 'Name' in doc:
            item_parts.append(f"📝 الاسم: {doc['Name']}")
        
        # السعر دائماً موجود
        if 'Price' in doc:
            item_parts.append(f"💰 السعر: {doc['Price']}")
        
        # المكونات حسب الإعدادات
        if config['ingredients_enabled'] and 'ingredients' in doc:
            ingredients = doc['ingredients']
            if ingredients and ingredients.strip():
                item_parts.append(f"🥗 المكونات: {ingredients}")
        
        # الوصف في الوضع الكامل
        if config['mode'] == 'full_details' and 'Description' in doc:
            description = doc['Description']
            if description and description.strip():
                item_parts.append(f"📋 الوصف: {description}")
        
        if item_parts:
            result_parts.append("\n".join(item_parts))
    
    if result_parts:
        return "\n\n" + "\n\n---\n\n".join(result_parts)
    else:
        return "لم يتم العثور على نتائج مطابقة لبحثك."
