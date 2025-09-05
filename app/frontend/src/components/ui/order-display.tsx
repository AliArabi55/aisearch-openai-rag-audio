import React from "react";
import { OrderItem } from "../../types";

interface OrderDisplayProps {
    orderItems: OrderItem[];
    totalPrice: number;
    isVisible: boolean;
}

const OrderDisplay: React.FC<OrderDisplayProps> = ({ orderItems, totalPrice, isVisible }) => {
    console.log("🎨 OrderDisplay Props:", { orderItems, totalPrice, isVisible });
    
    if (!isVisible) {
        console.log("❌ OrderDisplay hidden (isVisible=false)");
        return null;
    }

    console.log("✅ OrderDisplay rendering with", orderItems.length, "items");

    return (
        <div className="order-display-container">
            <h3 className="order-title">🛒 طلبك الحالي</h3>
            <div className="order-table-wrapper">
                <table className="order-table">
                    <thead>
                        <tr>
                            <th>العدد</th>
                            <th>اسم المنتج</th>
                            <th>السعر</th>
                            <th>الإجمالي</th>
                        </tr>
                    </thead>
                    <tbody>
                        {orderItems.length === 0 ? (
                            <tr>
                                <td colSpan={4} style={{ textAlign: 'center', padding: '20px', color: '#64748b' }}>
                                    لا توجد عناصر في الطلب بعد
                                </td>
                            </tr>
                        ) : (
                            orderItems.map((item, index) => (
                                <tr key={index}>
                                    <td className="quantity">{item.quantity}</td>
                                    <td className="name">{item.name}</td>
                                    <td className="price">{item.price} جنيه</td>
                                    <td className="total">{(item.price * item.quantity)} جنيه</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                    {orderItems.length > 0 && (
                        <tfoot>
                            <tr className="total-row">
                                <td colSpan={3}>
                                    <strong>الإجمالي الكلي</strong>
                                </td>
                                <td className="total-price">
                                    <strong>{totalPrice} جنيه</strong>
                                </td>
                            </tr>
                        </tfoot>
                    )}
                </table>
            </div>

            <style>{`
                .order-display-container {
                    width: 100%;
                    max-width: 600px;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
                    padding: 20px;
                    margin: 20px auto;
                    backdrop-filter: blur(10px);
                    border: 2px solid #e2e8f0;
                    animation: slideDown 0.3s ease-out;
                }
                
                @keyframes slideDown {
                    from {
                        transform: translateY(-20px);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
                
                .order-title {
                    color: #2d5aa0;
                    text-align: center;
                    margin-bottom: 15px;
                    font-size: 1.4em;
                    font-weight: bold;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .order-table-wrapper {
                    max-height: 300px;
                    overflow-y: auto;
                    border-radius: 10px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                }
                
                .order-table {
                    width: 100%;
                    border-collapse: collapse;
                    background: white;
                    font-size: 1em;
                }
                
                .order-table th {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 8px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 0.85em;
                    position: sticky;
                    top: 0;
                    z-index: 10;
                }
                
                .order-table td {
                    padding: 10px 8px;
                    text-align: center;
                    border-bottom: 1px solid #f1f5f9;
                    vertical-align: middle;
                }
                
                .order-table tbody tr:hover {
                    background: linear-gradient(90deg, #f8fafc, #e2e8f0);
                }
                
                .quantity {
                    background: linear-gradient(135deg, #4facfe, #00f2fe);
                    color: white;
                    font-weight: bold;
                    border-radius: 50%;
                    width: 35px;
                    height: 35px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto;
                    box-shadow: 0 2px 5px rgba(79, 172, 254, 0.3);
                }
                
                .name {
                    font-weight: bold;
                    color: #1e293b;
                    text-align: right;
                    font-size: 0.9em;
                }
                
                .price, .total {
                    font-weight: bold;
                    color: #059669;
                    font-family: 'Courier New', monospace;
                }
                
                .ingredients {
                    font-size: 0.8em;
                    color: #64748b;
                    text-align: right;
                    max-width: 150px;
                    line-height: 1.2;
                    word-wrap: break-word;
                }
                
                .total-row {
                    background: linear-gradient(135deg, #10b981, #059669) !important;
                    color: white !important;
                }
                
                .total-row td {
                    font-size: 1.05em;
                    font-weight: bold;
                    padding: 15px 8px;
                    border-bottom: none;
                }
                
                .total-price {
                    font-size: 1.1em;
                    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
                }
                
                /* Responsive design */
                @media (max-width: 768px) {
                    .order-display-container {
                        position: static;
                        max-width: 100%;
                        margin: 20px;
                        right: auto;
                        top: auto;
                    }
                    
                    .order-table {
                        font-size: 0.8em;
                    }
                    
                    .order-table th,
                    .order-table td {
                        padding: 8px 4px;
                    }
                    
                    .ingredients {
                        max-width: 100px;
                        font-size: 0.7em;
                    }
                }
                
                /* Custom scrollbar */
                .order-table-wrapper::-webkit-scrollbar {
                    width: 8px;
                }
                
                .order-table-wrapper::-webkit-scrollbar-track {
                    background: #f1f5f9;
                    border-radius: 4px;
                }
                
                .order-table-wrapper::-webkit-scrollbar-thumb {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    border-radius: 4px;
                }
                
                .order-table-wrapper::-webkit-scrollbar-thumb:hover {
                    background: linear-gradient(135deg, #5a67d8, #6b46c1);
                }
            `}</style>
        </div>
    );
};

export default OrderDisplay;
