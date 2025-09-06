# -*- coding: utf-8 -*-
"""
نظام إدارة الطلبات للمطعم
Order Management System for Restaurant
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class OrderItem:
    """عنصر في الطلب"""
    id: str
    name: str
    price: float
    ingredients: str
    quantity: int = 1
    
    def get_total_price(self) -> float:
        """حساب السعر الإجمالي للعنصر"""
        return self.price * self.quantity
    
    def to_dict(self) -> Dict:
        """تحويل إلى dictionary"""
        return asdict(self)

class OrderManager:
    """مدير الطلبات"""
    
    def __init__(self):
        self.current_order: List[OrderItem] = []
        self.order_history: List[Dict] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_item(self, item_data: Dict) -> Tuple[bool, str]:
        """
        إضافة عنصر للطلب
        Returns: (success, message)
        """
        try:
            # استخراج البيانات من نتيجة البحث
            item_id = item_data.get('ID', '')
            name = item_data.get('Name', '')
            ingredients = item_data.get('ingredients', '')
            price_str = item_data.get('Price', '0')
            
            # تنظيف السعر (إزالة كلمة "جنيه" أو أي نص)
            price = self._extract_price(price_str)
            
            if not name or price <= 0:
                return False, "بيانات المنتج غير مكتملة"
            
            # البحث عن العنصر في الطلب الحالي
            existing_item = self._find_existing_item(item_id, name)
            
            if existing_item:
                # زيادة الكمية
                existing_item.quantity += 1
                message = f"تم زيادة {name} إلى {existing_item.quantity}"
            else:
                # إضافة عنصر جديد
                new_item = OrderItem(
                    id=item_id,
                    name=name,
                    price=price,
                    ingredients=ingredients,
                    quantity=1
                )
                self.current_order.append(new_item)
                message = f"تم إضافة {name} للطلب"
            
            return True, message
            
        except Exception as e:
            return False, f"خطأ في إضافة المنتج: {str(e)}"
    
    def remove_item(self, item_name: str) -> Tuple[bool, str]:
        """حذف عنصر من الطلب"""
        for i, item in enumerate(self.current_order):
            if item_name.lower() in item.name.lower():
                removed_item = self.current_order.pop(i)
                return True, f"تم حذف {removed_item.name} من الطلب"
        
        return False, f"لم أجد {item_name} في الطلب"
    
    def update_quantity(self, item_name: str, new_quantity: int) -> Tuple[bool, str]:
        """تحديث كمية عنصر"""
        for item in self.current_order:
            if item_name.lower() in item.name.lower():
                if new_quantity <= 0:
                    return self.remove_item(item_name)
                else:
                    item.quantity = new_quantity
                    return True, f"تم تحديث كمية {item.name} إلى {new_quantity}"
        
        return False, f"لم أجد {item_name} في الطلب"
    
    def get_order_summary(self) -> Dict:
        """ملخص الطلب الحالي"""
        if not self.current_order:
            return {
                "items": [],
                "total_items": 0,
                "total_price": 0,
                "formatted_summary": "الطلب فارغ",
                "table_html": "<p>لا توجد طلبات</p>"
            }
        
        total_price = sum(item.get_total_price() for item in self.current_order)
        total_items = sum(item.quantity for item in self.current_order)
        
        # إنشاء ملخص نصي
        summary_text = "📋 **ملخص الطلب:**\n\n"
        for item in self.current_order:
            summary_text += f"🍽️ {item.quantity}x {item.name}\n"
            summary_text += f"   المكونات: {item.ingredients}\n"
            summary_text += f"   السعر: {item.price} × {item.quantity} = {item.get_total_price()} جنيه\n\n"
        
        summary_text += f"📊 **الإجمالي:** {total_price} جنيه\n"
        summary_text += f"📝 **عدد الأصناف:** {total_items} قطعة"
        
        # إنشاء جدول HTML
        table_html = self._create_order_table()
        
        return {
            "items": [item.to_dict() for item in self.current_order],
            "total_items": total_items,
            "total_price": total_price,
            "formatted_summary": summary_text,
            "table_html": table_html
        }
    
    def clear_order(self) -> str:
        """مسح الطلب الحالي"""
        if self.current_order:
            # حفظ في التاريخ
            self.order_history.append({
                "timestamp": datetime.now().isoformat(),
                "items": [item.to_dict() for item in self.current_order],
                "total_price": sum(item.get_total_price() for item in self.current_order)
            })
        
        self.current_order.clear()
        return "تم مسح الطلب"
    
    def confirm_order(self) -> Tuple[bool, str, Dict]:
        """تأكيد الطلب"""
        if not self.current_order:
            return False, "الطلب فارغ", {}
        
        order_summary = self.get_order_summary()
        
        # حفظ الطلب المؤكد
        confirmed_order = {
            "order_id": f"ORD_{self.session_id}_{len(self.order_history) + 1}",
            "timestamp": datetime.now().isoformat(),
            "items": order_summary["items"],
            "total_price": order_summary["total_price"],
            "status": "confirmed"
        }
        
        self.order_history.append(confirmed_order)
        self.current_order.clear()
        
        confirmation_text = f"""
✅ **تم تأكيد الطلب!**

رقم الطلب: {confirmed_order['order_id']}
الإجمالي: {order_summary['total_price']} جنيه
الأوردر هيكون جاهز خلال نص ساعة
شكراً لك في مطعم سيركلز! 🍕
        """.strip()
        
        return True, confirmation_text, confirmed_order
    
    def _extract_price(self, price_str: str) -> float:
        """استخراج السعر من النص"""
        if isinstance(price_str, (int, float)):
            return float(price_str)
        
        # إزالة النصوص وإبقاء الأرقام فقط
        price_match = re.search(r'[\d.]+', str(price_str))
        if price_match:
            return float(price_match.group())
        
        return 0.0
    
    def _find_existing_item(self, item_id: str, name: str) -> Optional[OrderItem]:
        """البحث عن عنصر موجود في الطلب"""
        for item in self.current_order:
            if item.id == item_id or item.name == name:
                return item
        return None
    
    def _create_order_table(self) -> str:
        """إنشاء جدول HTML للطلب"""
        if not self.current_order:
            return """
            <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 20px; color: white;">
                <h3 style="margin: 0; font-size: 24px;">🍽️ لا توجد طلبات حالياً</h3>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">ابدأ طلبك الآن من مطعم سيركلز!</p>
            </div>
            """
        
        table_html = """
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin: 20px; padding: 25px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            <div style="text-align: center; margin-bottom: 25px; padding-bottom: 20px; border-bottom: 2px solid rgba(255,255,255,0.3);">
                <h2 style="color: white; margin: 0; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🍽️ Order your food now from Circles Restaurant</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">استمتع بأشهى الأطباق من مطعم سيركلز</p>
            </div>
            <div style="background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.2);">
                <table style="width: 100%; border-collapse: collapse; margin: 0;">
                    <thead>
                        <tr style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white;">
                            <th style="padding: 18px 15px; text-align: right; font-size: 16px; font-weight: bold;">الصنف</th>
                            <th style="padding: 18px 15px; text-align: center; font-size: 16px; font-weight: bold;">الكمية</th>
                            <th style="padding: 18px 15px; text-align: center; font-size: 16px; font-weight: bold;">السعر</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # إضافة كل صنف في الطلب
        for i, item in enumerate(self.current_order):
            bg_color = "#f8f9fa" if i % 2 == 0 else "#ffffff"
            table_html += f"""
                    <tr style="background: {bg_color}; transition: all 0.3s ease;">
                        <td style="padding: 18px 15px; text-align: right; font-weight: bold; color: #2c3e50; font-size: 16px; border-bottom: 1px solid #e9ecef;">{item.name}</td>
                        <td style="padding: 18px 15px; text-align: center;">
                            <span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px;">{item.quantity}</span>
                        </td>
                        <td style="padding: 18px 15px; text-align: center; color: #27ae60; font-weight: bold; font-size: 16px; border-bottom: 1px solid #e9ecef;">{item.get_total_price():.0f} ج</td>
                    </tr>
            """
        
        total_price = sum(item.get_total_price() for item in self.current_order)
        total_items = sum(item.quantity for item in self.current_order)
        
        table_html += f"""
                    </tbody>
                    <tfoot>
                        <tr style="background: linear-gradient(135deg, #2c3e50, #34495e); color: white;">
                            <td style="padding: 25px 15px; text-align: right; font-size: 18px; font-weight: bold;">المجموع ({total_items} قطعة)</td>
                            <td style="padding: 25px 15px; text-align: center; font-size: 18px; font-weight: bold;">🛒</td>
                            <td style="padding: 25px 15px; text-align: center; font-size: 22px; font-weight: bold; color: #f39c12;">{total_price:.0f} جنيه</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            <div style="text-align: center; margin-top: 25px; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 15px; backdrop-filter: blur(10px);">
                <p style="color: white; margin: 0; font-style: italic; font-size: 16px;">🕐 سيتم تحضير طلبك في خلال 20-30 دقيقة</p>
                <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0; font-size: 14px;">شكراً لاختيارك مطعم سيركلز</p>
            </div>
        </div>
        """
        
        return table_html

# Global order manager instance
order_manager = OrderManager()

# 🆕 Helper functions for ragtools integration
def add_to_current_order(item_id: str, name: str, price: float, quantity: int = 1) -> dict:
    """إضافة عنصر للطلب الحالي وإرجاع الملخص"""
    try:
        # تحضير بيانات العنصر
        item_data = {
            'ID': item_id,
            'Name': name,
            'Price': str(price),
            'ingredients': '',  # يمكن إضافتها لاحقاً
            'quantity': quantity
        }
        
        success, message = order_manager.add_item(item_data)
        
        if success:
            # إرجاع ملخص الطلب المحدث
            return get_current_order_summary()
        else:
            return {
                "action": "order_error",
                "message": f"فشل في إضافة {name}: {message}"
            }
    except Exception as e:
        return {
            "action": "order_error", 
            "message": f"خطأ في إضافة العنصر: {e}"
        }

def get_current_order_summary() -> dict:
    """الحصول على ملخص الطلب الحالي"""
    try:
        if order_manager.is_empty():
            return {
                "action": "order_updated",
                "order_summary": {
                    "items": [],
                    "total_price": 0,
                    "item_count": 0
                }
            }
        
        # تحضير قائمة العناصر
        items = []
        for item in order_manager.current_order:
            items.append({
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "quantity": item.quantity,
                "total": item.get_total_price()
            })
        
        return {
            "action": "order_updated",
            "order_summary": {
                "items": items,
                "total_price": order_manager.get_total_price(),
                "item_count": len(order_manager.current_order)
            }
        }
    except Exception as e:
        return {
            "action": "order_error",
            "message": f"خطأ في جلب ملخص الطلب: {e}"
        }

def confirm_current_order() -> dict:
    """تأكيد الطلب الحالي"""
    try:
        if order_manager.is_empty():
            return {
                "action": "order_error",
                "message": "لا يوجد عناصر في الطلب للتأكيد"
            }
        
        # حفظ الطلب وإرجاع رسالة التأكيد
        total_price = order_manager.get_total_price()
        item_count = len(order_manager.current_order)
        
        # مسح الطلب الحالي (simulate confirmation)
        order_manager.current_order.clear()
        
        return {
            "action": "order_confirmed",
            "message": f"تم تأكيد طلبك بنجاح! الإجمالي: {total_price:.0f} جنيه ({item_count} عناصر)",
            "order_summary": {
                "items": [],
                "total_price": 0,
                "item_count": 0
            }
        }
    except Exception as e:
        return {
            "action": "order_error",
            "message": f"خطأ في تأكيد الطلب: {e}"
        }

def clear_current_order() -> dict:
    """مسح الطلب الحالي"""
    try:
        order_manager.current_order.clear()
        return {
            "action": "order_cleared", 
            "message": "تم مسح الطلب",
            "order_summary": {
                "items": [],
                "total_price": 0,
                "item_count": 0
            }
        }
    except Exception as e:
        return {
            "action": "order_error",
            "message": f"خطأ في مسح الطلب: {e}"
        }
