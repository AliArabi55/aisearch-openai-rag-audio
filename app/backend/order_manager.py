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
            return "<div class='order-empty'>لا توجد طلبات</div>"
        
        table_html = """
        <div class="order-table-container">
            <h3 class="order-title">🛒 الطلب الحالي</h3>
            <table class="order-table">
                <thead>
                    <tr>
                        <th>العدد</th>
                        <th>اسم المنتج</th>
                        <th>السعر</th>
                        <th>المكونات</th>
                        <th>الإجمالي</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_price = 0
        for item in self.current_order:
            item_total = item.get_total_price()
            total_price += item_total
            
            table_html += f"""
                    <tr>
                        <td class="quantity">{item.quantity}</td>
                        <td class="name">{item.name}</td>
                        <td class="price">{item.price} ج</td>
                        <td class="ingredients">{item.ingredients}</td>
                        <td class="total">{item_total} ج</td>
                    </tr>
            """
        
        table_html += f"""
                </tbody>
                <tfoot>
                    <tr class="total-row">
                        <td colspan="4"><strong>الإجمالي</strong></td>
                        <td class="total-price"><strong>{total_price} ج</strong></td>
                    </tr>
                </tfoot>
            </table>
        </div>
        
        <style>
        .order-table-container {{
            margin: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .order-title {{
            color: #2d5aa0;
            text-align: center;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .order-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .order-table th {{
            background: #2d5aa0;
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: bold;
        }}
        
        .order-table td {{
            padding: 10px 8px;
            text-align: center;
            border-bottom: 1px solid #eee;
        }}
        
        .order-table tr:hover {{
            background: #f5f5f5;
        }}
        
        .quantity {{
            background: #007bff;
            color: white;
            font-weight: bold;
            border-radius: 15px;
            width: 30px;
        }}
        
        .name {{
            font-weight: bold;
            color: #333;
            text-align: right;
        }}
        
        .price, .total {{
            font-weight: bold;
            color: #28a745;
        }}
        
        .ingredients {{
            font-size: 0.9em;
            color: #666;
            text-align: right;
            max-width: 200px;
        }}
        
        .total-row {{
            background: #28a745 !important;
            color: white !important;
        }}
        
        .total-row td {{
            font-size: 1.1em;
            font-weight: bold;
        }}
        
        .order-empty {{
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 20px;
        }}
        </style>
        """
        
        return table_html

# Global order manager instance
order_manager = OrderManager()
