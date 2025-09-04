#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشخيص مشكلة البحث الدلالي وحلولها
Diagnosing Semantic Search Issues and Solutions
"""

import os
import sys
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def print_arabic(text):
    """طباعة النصوص العربية بشكل صحيح"""
    try:
        print(text.encode('utf-8').decode('utf-8'))
    except:
        print(text)

class SemanticSearchDiagnostic:
    def __init__(self):
        # تحميل متغيرات البيئة
        load_dotenv("app/backend/.env")
        
        self.search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.environ.get("AZURE_SEARCH_API_KEY")
        self.search_index = os.environ.get("AZURE_SEARCH_INDEX")
        self.semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
        
        print_arabic("🔍 تشخيص مشكلة البحث الدلالي")
        print_arabic("=" * 50)
        print_arabic(f"🔗 النقطة النهاية: {self.search_endpoint}")
        print_arabic(f"📋 الفهرس: {self.search_index}")
        print_arabic(f"🧠 الإعداد المطلوب: {self.semantic_config}")
        
        if not all([self.search_endpoint, self.search_key, self.search_index]):
            raise ValueError("Missing required Azure Search configuration")
        
        self.credential = AzureKeyCredential(self.search_key)
        
        # محاولة الاتصال بـ Index Client
        try:
            self.index_client = SearchIndexClient(
                endpoint=self.search_endpoint,
                credential=self.credential
            )
            print_arabic("✅ تم إنشاء Index Client بنجاح")
        except Exception as e:
            print_arabic(f"❌ خطأ في إنشاء Index Client: {str(e)}")
            self.index_client = None
    
    def diagnose_semantic_search(self):
        """تشخيص حالة البحث الدلالي"""
        print_arabic(f"\n🔬 تشخيص البحث الدلالي...")
        
        issues = []
        solutions = []
        
        # التحقق من الاتصال بالفهرس
        try:
            if self.index_client:
                index = self.index_client.get_index(self.search_index)
                print_arabic(f"✅ تم الوصول للفهرس بنجاح")
                
                # التحقق من البحث الدلالي
                if index.semantic_search:
                    print_arabic(f"✅ البحث الدلالي مفعل في الفهرس")
                    
                    if index.semantic_search.configurations:
                        print_arabic(f"📊 عدد الإعدادات المتاحة: {len(index.semantic_search.configurations)}")
                        
                        # عرض الإعدادات المتاحة
                        available_configs = []
                        for config in index.semantic_search.configurations:
                            available_configs.append(config.name)
                            print_arabic(f"   🔧 متاح: {config.name}")
                        
                        # التحقق من الإعداد المطلوب
                        if self.semantic_config in available_configs:
                            print_arabic(f"✅ الإعداد {self.semantic_config} موجود!")
                            return [], []  # لا توجد مشاكل
                        else:
                            issues.append(f"الإعداد '{self.semantic_config}' غير موجود")
                            solutions.append(f"استخدم أحد الإعدادات المتاحة: {', '.join(available_configs)}")
                            return issues, solutions, available_configs
                    else:
                        issues.append("لا توجد إعدادات بحث دلالي مُعرّفة")
                        solutions.append("أنشئ إعداد بحث دلالي في Azure Portal")
                else:
                    issues.append("البحث الدلالي غير مفعل في الفهرس")
                    solutions.append("فعّل البحث الدلالي من Azure Portal")
            else:
                issues.append("لا يمكن الوصول للفهرس")
                solutions.append("تحقق من مفاتيح الـ API")
                
        except Exception as e:
            error_msg = str(e)
            if "doesn't match service's internal" in error_msg:
                issues.append("مفتاح API خاطئ للوصول لإعدادات الفهرس")
                solutions.append("استخدم مفتاح Admin للوصول لإعدادات الفهرس")
            else:
                issues.append(f"خطأ في الاتصال: {error_msg}")
                solutions.append("تحقق من صحة الإعدادات")
        
        return issues, solutions, []
    
    def suggest_fixes(self, issues, solutions, available_configs=None):
        """اقتراح الحلول"""
        print_arabic(f"\n🚨 المشاكل المكتشفة:")
        for i, issue in enumerate(issues, 1):
            print_arabic(f"   {i}. {issue}")
        
        print_arabic(f"\n💡 الحلول المقترحة:")
        for i, solution in enumerate(solutions, 1):
            print_arabic(f"   {i}. {solution}")
        
        if available_configs:
            print_arabic(f"\n🔧 حل سريع - قم بتحديث ملف .env:")
            best_config = available_configs[0]
            print_arabic(f"   AZURE_SEARCH_SEMANTIC_CONFIGURATION={best_config}")
            
            # إنشاء ملف تحديث
            update_content = f"""
# تحديث إعدادات البحث الدلالي
# تغيير الإعداد من: {self.semantic_config}
# إلى الإعداد المتاح: {best_config}

AZURE_SEARCH_SEMANTIC_CONFIGURATION={best_config}
"""
            
            with open("semantic_config_update.txt", "w", encoding="utf-8") as f:
                f.write(update_content)
            
            print_arabic(f"📄 تم حفظ التحديث في: semantic_config_update.txt")
            return best_config
        
        return None

def main():
    """الدالة الرئيسية"""
    try:
        diagnostic = SemanticSearchDiagnostic()
        issues, solutions, available_configs = diagnostic.diagnose_semantic_search()
        
        if not issues:
            print_arabic(f"\n🎉 البحث الدلالي يجب أن يعمل!")
        else:
            suggested_config = diagnostic.suggest_fixes(issues, solutions, available_configs)
            
            if suggested_config:
                print_arabic(f"\n✅ يمكن إصلاح المشكلة باستخدام: {suggested_config}")
            else:
                print_arabic(f"\n⚠️  يحتاج تدخل في Azure Portal")
        
    except Exception as e:
        print_arabic(f"❌ خطأ عام: {str(e)}")

if __name__ == "__main__":
    main()
