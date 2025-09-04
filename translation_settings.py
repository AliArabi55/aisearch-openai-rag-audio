# إعدادات الترجمة
# Translation Settings Configuration

class TranslationSettings:
    """
    إعدادات التحكم في نظام الترجمة - خيارين فقط
    """
    
    # تفعيل/إيقاف الترجمة قبل البحث في AI Search
    # True = ترجمة النص العربي إلى إنجليزي قبل البحث (الافتراضي)
    # False = استخدام النص العربي مباشرة في البحث
    ENABLE_TRANSLATION = True
    
    @classmethod
    def get_mode(cls):
        """إرجاع الوضع الحالي للترجمة"""
        if cls.ENABLE_TRANSLATION:
            return "ترجمة من العربي للإنجليزي"
        else:
            return "بدون ترجمة (عربي مباشر)"
    
    @classmethod
    def is_translation_enabled(cls):
        """التحقق من حالة تفعيل الترجمة"""
        return cls.ENABLE_TRANSLATION
    
    @classmethod
    def toggle_translation(cls):
        """تبديل حالة الترجمة بين الوضعين"""
        cls.ENABLE_TRANSLATION = not cls.ENABLE_TRANSLATION
        return cls.get_mode()

def get_translation_settings():
    """الحصول على إعدادات الترجمة"""
    return TranslationSettings()

# للاستخدام السريع:
# من translation_settings import TranslationSettings
# print(TranslationSettings.ENABLE_TRANSLATION)  # True أو False
# TranslationSettings.ENABLE_TRANSLATION = False  # لإيقاف الترجمة

# الوضعان المتاحان:
# 1. ترجمة من العربي للإنجليزي (ENABLE_TRANSLATION = True) - الافتراضي
# 2. بدون ترجمة عربي مباشر (ENABLE_TRANSLATION = False)
