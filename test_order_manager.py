# -*- coding: utf-8 -*-
"""
اختبار نظام إدارة الطلبات
Order Management System Test
"""

import asyncio
import sys
import os

# إضافة مسار backend للمسار
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from order_manager import OrderManager

def test_order_manager():
    """اختبار مدير الطلبات"""
    print("🧪 اختبار نظام إدارة الطلبات")
    print("=" * 50)
    
    # إنشاء مدير طلبات جديد
    manager = OrderManager()
    
    # اختبار إضافة منتج
    item_data = {
        'ID': '1',
        'Name': 'بيتزا فراخ كبيرة',
        'ingredients': 'صلصة - فراخ - موتزريلا - فلفل',
        'Price': '120'
    }
    
    print("\n📝 إضافة منتج للطلب:")
    success, message = manager.add_item(item_data)
    print(f"✅ {message}" if success else f"❌ {message}")
    
    # إضافة منتج آخر
    item_data2 = {
        'ID': '2', 
        'Name': 'كوكا كولا',
        'ingredients': 'مشروب غازي',
        'Price': '15'
    }
    
    print("\n📝 إضافة منتج آخر:")
    success, message = manager.add_item(item_data2)
    print(f"✅ {message}" if success else f"❌ {message}")
    
    # إضافة نفس المنتج الأول مرة أخرى لاختبار زيادة الكمية
    print("\n📝 إضافة نفس المنتج مرة أخرى:")
    success, message = manager.add_item(item_data)
    print(f"✅ {message}" if success else f"❌ {message}")
    
    # عرض ملخص الطلب
    print("\n📋 ملخص الطلب:")
    summary = manager.get_order_summary()
    print(summary['formatted_summary'])
    
    # عرض جدول HTML (النسخة النصية)
    print("\n🌐 جدول HTML:")
    html_table = summary['table_html']
    # عرض أول 300 حرف فقط للاختبار
    print(html_table[:300] + "..." if len(html_table) > 300 else html_table)
    
    # تأكيد الطلب
    print("\n✅ تأكيد الطلب:")
    success, confirmation, order_details = manager.confirm_order()
    if success:
        print(confirmation)
        print(f"رقم الطلب: {order_details['order_id']}")
    else:
        print(f"❌ {confirmation}")
    
    print("\n🎉 انتهى الاختبار بنجاح!")

if __name__ == "__main__":
    test_order_manager()
