#!/usr/bin/env python3
"""
order_tools.py - أدوات إدارة الطلبات للموديل
Order Management Tools for AI Model
"""

import json
import re
from typing import Any
from rtmt import ToolResult, ToolResultDirection, Tool
from order_manager import (
    order_manager, 
    add_to_current_order, 
    get_current_order_summary, 
    confirm_current_order, 
    clear_current_order
)

def register_order_tools(rtmt):
    """تسجيل أدوات إدارة الطلبات في النظام"""
    
    # 🆕 أداة تأكيد الطلب
    confirm_order_schema = {
        "type": "function",
        "name": "confirm_order",
        "description": "تأكيد الطلب الحالي وإتمام الشراء",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    async def confirm_order_wrapper(args: Any) -> ToolResult:
        """تأكيد الطلب"""
        try:
            result = confirm_current_order()
            return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
        except Exception as e:
            return ToolResult(f"خطأ في تأكيد الطلب: {e}", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["confirm_order"] = Tool(schema=confirm_order_schema, target=confirm_order_wrapper)
    
    # 🆕 أداة إضافة عنصر محدد للطلب
    add_item_to_order_schema = {
        "type": "function", 
        "name": "add_item_to_order",
        "description": "إضافة عنصر محدد للطلب بعد البحث عنه وتأكيد الرغبة من المستخدم",
        "parameters": {
            "type": "object",
            "properties": {
                "item_id": {"type": "string", "description": "معرف العنصر"},
                "item_name": {"type": "string", "description": "اسم العنصر"},
                "price": {"type": "string", "description": "سعر العنصر"},
                "quantity": {"type": "integer", "description": "الكمية المطلوبة", "default": 1}
            },
            "required": ["item_id", "item_name", "price"]
        }
    }
    
    async def add_item_to_order_wrapper(args: Any) -> ToolResult:
        """إضافة عنصر للطلب"""
        try:
            item_id = args.get("item_id", "")
            item_name = args.get("item_name", "")
            price_str = args.get("price", "0")
            quantity = args.get("quantity", 1)
            
            # تنظيف السعر
            price = float(re.sub(r'[^\d.]', '', str(price_str)))
            
            result = add_to_current_order(item_id, item_name, price, quantity)
            return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
        except Exception as e:
            return ToolResult(f"خطأ في إضافة العنصر: {e}", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["add_item_to_order"] = Tool(schema=add_item_to_order_schema, target=add_item_to_order_wrapper)
    
    # 🆕 أداة عرض الطلب الحالي
    show_current_order_schema = {
        "type": "function",
        "name": "show_current_order", 
        "description": "عرض الطلب الحالي مع التفاصيل والإجمالي",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    async def show_current_order_wrapper(args: Any) -> ToolResult:
        """عرض الطلب الحالي"""
        try:
            result = get_current_order_summary()
            return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
        except Exception as e:
            return ToolResult(f"خطأ في عرض الطلب: {e}", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["show_current_order"] = Tool(schema=show_current_order_schema, target=show_current_order_wrapper)
    
    # 🆕 أداة اكتشاف كلمات الإنهاء
    check_goodbye_schema = {
        "type": "function",
        "name": "check_goodbye",
        "description": "فحص إذا كان المستخدم يريد إنهاء المحادثة (سلام، مع السلامة، إلى اللقاء)",
        "parameters": {
            "type": "object",
            "properties": {
                "user_message": {"type": "string", "description": "رسالة المستخدم للفحص"}
            },
            "required": ["user_message"]
        }
    }
    
    async def check_goodbye_wrapper(args: Any) -> ToolResult:
        """فحص كلمات الإنهاء"""
        try:
            user_message = args.get("user_message", "").lower().strip()
            
            # كلمات الإنهاء المحدثة
            goodbye_words = [
                "سلام", "مع السلامة", "إلى اللقاء", "إلي اللقاء", "إلى للقاء",
                "باي", "goodbye", "bye", "سلامه", "اللقاء", "وداع",
                "خلاص", "كفاية", "انتهيت", "مش محتاج حاجة تاني",
                "هو ده كل حاجة", "كده تمام", "اشوفك قريب", "ربنا معاكم"
            ]
            
            print(f"🔍 فحص كلمات الإنهاء في: '{user_message}'")
            
            for word in goodbye_words:
                if word in user_message:
                    print(f"✅ تم اكتشاف كلمة إنهاء: '{word}'")
                    # مسح الذاكرة المؤقتة عند الإنهاء
                    from ragtools import clear_cache
                    clear_cache()
                    result = {
                        "action": "end_conversation",
                        "message": "شكراً لك! تم إنهاء المحادثة. نتطلع لخدمتك مرة أخرى.",
                        "should_disconnect": True
                    }
                    print("🔚 إرسال أمر إنهاء المحادثة")
                    return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
            
            print("➡️ لا توجد كلمات إنهاء، المحادثة مستمرة")
            result = {
                "action": "continue_conversation", 
                "should_disconnect": False
            }
            return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
            
        except Exception as e:
            return ToolResult(f"خطأ في فحص الإنهاء: {e}", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["check_goodbye"] = Tool(schema=check_goodbye_schema, target=check_goodbye_wrapper)
    
    print("🛒 تم تسجيل أدوات إدارة الطلبات: confirm_order, add_item_to_order, show_current_order, check_goodbye")
