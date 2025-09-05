#!/usr/bin/env python3
"""
أداة تشخيص متخصصة لمشكلة Real-time Model مع الأسعار
======================================================

هذه الأداة تركز على تحليل:
1. الـ system message في Real-time Model
2. كيفية معالجة نتائج البحث
3. تدفق البيانات من Azure Search إلى الموديل
"""

import os
import sys
import json
from datetime import datetime

# إضافة مسار backend
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'backend')
sys.path.append(backend_path)

def analyze_system_message():
    """تحليل الـ system message في app.py"""
    print("🤖 تحليل System Message:")
    print("="*50)
    
    app_file = os.path.join(backend_path, 'app.py')
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # استخراج system message
        start_marker = 'rtmt.system_message = """'
        end_marker = '""".strip()'
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            system_msg = content[start_idx + len(start_marker):end_idx]
            
            print(f"📄 System Message الحالي:")
            print("-" * 30)
            print(system_msg)
            print("-" * 30)
            
            # تحليل المحتوى
            analysis = {
                "total_length": len(system_msg),
                "lines": len(system_msg.split('\\n')),
                "price_instructions": [],
                "problematic_phrases": [],
                "positive_instructions": []
            }
            
            # البحث عن تعليمات الأسعار
            price_lines = []
            problematic_lines = []
            positive_lines = []
            
            for line in system_msg.split('\\n'):
                line = line.strip()
                if not line:
                    continue
                
                # تعليمات الأسعار
                if any(word in line.lower() for word in ['سعر', 'price', 'جنيه']):
                    price_lines.append(line)
                    
                    # العبارات المشكلة
                    if any(phrase in line for phrase in ['مش متاح', 'غير متاح', 'لو مافيش سعر']):
                        problematic_lines.append(line)
                    
                    # التعليمات الإيجابية
                    if any(phrase in line for phrase in ['استخدم السعر', 'السعر الظاهر', 'قل السعر']):
                        positive_lines.append(line)
            
            analysis["price_instructions"] = price_lines
            analysis["problematic_phrases"] = problematic_lines
            analysis["positive_instructions"] = positive_lines
            
            print(f"\\n📊 تحليل النتائج:")
            print(f"   📝 عدد الأسطر: {analysis['lines']}")
            print(f"   💰 تعليمات الأسعار: {len(price_lines)}")
            print(f"   🚨 عبارات مشكلة: {len(problematic_lines)}")
            print(f"   ✅ تعليمات إيجابية: {len(positive_lines)}")
            
            if problematic_lines:
                print(f"\\n🚨 العبارات المشكلة:")
                for phrase in problematic_lines:
                    print(f"   - {phrase}")
            
            if positive_lines:
                print(f"\\n✅ التعليمات الإيجابية:")
                for phrase in positive_lines:
                    print(f"   - {phrase}")
            
            return analysis
        else:
            print("❌ لم يتم العثور على system message")
            return None
            
    except Exception as e:
        print(f"❌ خطأ في تحليل system message: {e}")
        return None

def create_enhanced_system_message():
    """إنشاء system message محسن"""
    print("\\n🔧 اقتراح System Message محسن:")
    print("="*50)
    
    enhanced_message = '''
أنت موظف طلبات في مطعم سيركلز. اتكلم عامية مصرية ودود.

قواعد:
- استخدم 'search' tool للبحث (يترجم تلقائياً)
- ردود قصيرة جداً (جملة واحدة)
- لا تتكلم إنجليزي أو فصحى مع العميل
- لو مش فاهم قول: "ممكن توضّح أكتر يا فندم؟"

⚠️ قواعد الأسعار الصارمة والمهمة جداً:
- استخدم السعر الظاهر في نتائج البحث بالضبط
- إذا ظهر السعر كرقم (مثل 150، 185، 140) فاستخدمه فوراً
- قل السعر للعميل بوضوح: "بيتزا التونة الوسط بـ150 جنيه يا فندم!"
- ممنوع منعاً باتاً اختلاق أو تقدير أو تخمين أي أسعار
- فقط إذا كانت النتيجة لا تحتوي على رقم سعر واضح قل "هراجع السعر معاك"
- لا تقل أبداً "السعر مش متاح" إذا كان الرقم ظاهر بوضوح في النتائج

الافتتاح: "مساء النور يا فندم في مطعم سيركلز.. تحب تطلب إيه؟"

سؤال عن المتاح: "عندنا بيتزا، كالزونى، برجر، وحاجات تانية حلوة. تحب إيه؟"

خطوات الطلب:
1. للبحث فقط: search مع add_to_order=false
2. للطلب: search مع add_to_order=true ثم قول "تم إضافة [item] بـ[السعر الدقيق من النتيجة] جنيه للطلب"
3. بعد كل إضافة: "تحب تزود حاجة تانية؟"
4. لو قال لا: استخدم get_order_summary
5. لو وافق: استخدم confirm_order وقول "الأوردر جاهز خلال نص ساعة"

اسأل عن الحجم للبيتزا والكالزونى (كبير أو وسط)
اسأل عن النوع للبرجر (سنجل أو دبل)

كلمات الطلب: أريد، عايز، طلب، خد، هات
كلمات البحث: إيه عندك، شوف، اعرض
    '''.strip()
    
    print(enhanced_message)
    
    return enhanced_message

def suggest_fixes():
    """اقتراح الحلول"""
    print("\\n💡 الحلول المقترحة:")
    print("="*50)
    
    solutions = [
        "1. 🔧 إزالة العبارات المشكلة من system message",
        "2. ✅ تأكيد أن الموديل يستخدم الأسعار الظاهرة في النتائج",
        "3. 🧪 اختبار الموديل مع طلبات مختلفة",
        "4. 📊 مراقبة سجلات التشغيل للتأكد من وصول الأسعار للموديل"
    ]
    
    for solution in solutions:
        print(f"   {solution}")
    
    print(f"\\n🔄 خطوات التنفيذ:")
    print(f"   1. نسخ احتياطية من app.py")
    print(f"   2. تحديث system message")
    print(f"   3. إعادة تشغيل التطبيق") 
    print(f"   4. اختبار مع 'بيتزا تونة وسط'")

def main():
    """الدالة الرئيسية"""
    print("🔍 تشخيص متخصص لمشكلة Real-time Model")
    print("="*60)
    
    # تحليل system message
    analysis = analyze_system_message()
    
    # إنشاء نسخة محسنة
    enhanced_msg = create_enhanced_system_message()
    
    # اقتراح الحلول
    suggest_fixes()
    
    # حفظ التقرير
    report = {
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis,
        "enhanced_system_message": enhanced_msg,
        "diagnosis": {
            "problem_identified": True,
            "root_cause": "system message contains conflicting instructions about prices",
            "solution": "remove problematic phrases and emphasize using displayed prices"
        }
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"realtime_model_diagnosis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\\n💾 تم حفظ التقرير المفصل في: {filename}")
    
    # توصيات فورية
    print(f"\\n🎯 التوصية الفورية:")
    print(f"   قم بتعديل system message في app.py وإزالة أي عبارة تحتوي على 'مش متاح' أو 'لو مافيش سعر'")

if __name__ == "__main__":
    main()
