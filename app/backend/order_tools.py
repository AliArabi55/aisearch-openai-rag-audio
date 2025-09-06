# -*- coding: utf-8 -*-
"""
أدوات إدارة الطلبات
Order Tools for Restaurant Management
"""

from rtmt import Tool
from order_manager import OrderManager

# إنشاء مدير الطلبات العام
order_manager = OrderManager()

def register_order_tools(rtmt):
    """تسجيل أدوات الطلبات مع RTMT"""
    
    # أداة إضافة عنصر للطلب
    add_item_schema = {
        "type": "function",
        "name": "add_item_to_order",
        "description": "إضافة عنصر جديد للطلب الحالي",
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {"type": "string", "description": "اسم العنصر"},
                "quantity": {"type": "integer", "description": "الكمية", "default": 1}
            },
            "required": ["item_name"]
        }
    }
    
    def add_item_to_order_wrapper(item_name: str, quantity: int = 1):
        """إضافة عنصر للطلب"""
        try:
            result = order_manager.add_item_by_name(item_name, quantity)
            return {"success": True, "message": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # أداة عرض الطلب الحالي
    show_order_schema = {
        "type": "function", 
        "name": "show_current_order",
        "description": "عرض الطلب الحالي مع التفاصيل والسعر الإجمالي",
        "parameters": {"type": "object", "properties": {}, "required": []}
    }
    
    def show_current_order_wrapper():
        """عرض الطلب الحالي"""
        try:
            order_summary = order_manager.get_order_summary()
            return {"success": True, "order": order_summary}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # أداة تأكيد الطلب
    confirm_order_schema = {
        "type": "function",
        "name": "confirm_order", 
        "description": "تأكيد وإنهاء الطلب الحالي",
        "parameters": {"type": "object", "properties": {}, "required": []}
    }
    
    def confirm_order_wrapper():
        """تأكيد الطلب"""
        try:
            confirmation = order_manager.confirm_order()
            return {"success": True, "confirmation": confirmation}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # تسجيل الأدوات مع RTMT
    rtmt.tools["add_item_to_order"] = Tool(schema=add_item_schema, target=add_item_to_order_wrapper)
    rtmt.tools["show_current_order"] = Tool(schema=show_order_schema, target=show_current_order_wrapper)
    rtmt.tools["confirm_order"] = Tool(schema=confirm_order_schema, target=confirm_order_wrapper)
    
    print("✅ تم تسجيل أدوات الطلبات بنجاح")
