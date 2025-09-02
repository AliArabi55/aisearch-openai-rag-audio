# إعدادات الترجمة
# Translation Settings Configuration

class TranslationSettings:
    """
    إعدادات التحكم في نظام الترجمة
    """
    
    # تفعيل/إيقاف الترجمة قبل البحث في AI Search
    # True = ترجمة النص العربي إلى إنجليزي قبل البحث
    # False = استخدام النص العربي مباشرة في البحث
    ENABLE_TRANSLATION = True
    
    # تفعيل/إيقاف استخدام القاموس في الترجمة
    # True = استخدام القاموس المخصص للترجمة
    # False = استخدام الترجمة الآلية فقط (بدون قاموس)
    USE_DICTIONARY = True
    
    # إعدادات إضافية
    EXTRACT_FOOD_KEYWORDS_ONLY = True  # استخراج كلمات الطعام فقط
    SHOW_TRANSLATION_DEBUG = True      # إظهار معلومات الترجمة في الـ debug
    
    @classmethod
    def get_mode(cls):
        """إرجاع الوضع الحالي للترجمة"""
        if cls.ENABLE_TRANSLATION:
            if cls.USE_DICTIONARY:
                return "ترجمة مع القاموس"
            else:
                return "ترجمة بدون قاموس" 
        else:
            return "بدون ترجمة (عربي مباشر)"
    
    @classmethod
    def toggle_translation(cls):
        """تبديل حالة الترجمة"""
        cls.ENABLE_TRANSLATION = not cls.ENABLE_TRANSLATION
        return cls.get_mode()
    
    @classmethod
    def toggle_dictionary(cls):
        """تبديل استخدام القاموس"""
        cls.USE_DICTIONARY = not cls.USE_DICTIONARY
        return cls.get_mode()

def get_translation_settings():
    """الحصول على إعدادات الترجمة"""
    return TranslationSettings()

# للاستخدام السريع:
# من translation_settings import TranslationSettings
# print(TranslationSettings.ENABLE_TRANSLATION)  # True أو False
# TranslationSettings.ENABLE_TRANSLATION = False  # لإيقاف الترجمة
