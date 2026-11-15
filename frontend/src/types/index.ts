export type Role = 'MANAGER' | 'SALES_REP';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  address: string;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  name: string;
  sku: string;
  description?: string;
  price: string | number;
  stock_quantity: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type OrderStatus = 'PENDING_APPROVAL' | 'CONFIRMED' | 'APPROVED' | 'REJECTED' | 'CANCELLED';

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product_name?: string;
  product_sku?: string;
  quantity: number;
  unit_price: string | number;
  subtotal: string | number;
  created_at: string;
  updated_at: string;
}

export interface Order {
  id: number;
  order_number: string;
  customer_id: number;
  customer_name?: string;
  created_by_id: number;
  created_by_username?: string;
  total_amount: string | number;
  status: OrderStatus;
  reviewed_by_id?: number;
  reviewed_at?: string;
  approval_notes?: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface DashboardSummary {
  total_revenue: string | number;
  total_orders: number;
  orders_by_status: Record<string, number>;
  low_stock_count: number;
  recent_orders: Order[];
}

export interface StockAdjustment {
  product_id: number;
  previous_stock: number;
  change_quantity: number;
  new_stock: number;
}
