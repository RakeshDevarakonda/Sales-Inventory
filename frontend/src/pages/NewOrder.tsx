import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchCustomers } from '../store/slices/customerSlice';
import { fetchProducts } from '../store/slices/productSlice';
import { createOrder } from '../store/slices/orderSlice';
import { ShoppingCart, Plus, Trash2, ArrowLeft, AlertCircle, Info } from 'lucide-react';
import { Link } from 'react-router-dom';

interface OrderLineItem {
  product_id: number;
  quantity: number;
}

export default function NewOrder() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const { items: customers } = useAppSelector((state) => state.customers);
  const { items: products } = useAppSelector((state) => state.products);

  const [customerId, setCustomerId] = useState<number | ''>('');
  const [items, setItems] = useState<OrderLineItem[]>([
    { product_id: 0, quantity: 1 },
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchCustomers());
    dispatch(fetchProducts(true)); // only active products
  }, [dispatch]);

  const handleAddItem = () => {
    setItems([...items, { product_id: 0, quantity: 1 }]);
  };

  const handleRemoveItem = (index: number) => {
    if (items.length === 1) return;
    setItems(items.filter((_, idx) => idx !== index));
  };

  const handleItemChange = (index: number, field: 'product_id' | 'quantity', value: number) => {
    const updated = [...items];
    updated[index][field] = value;
    setItems(updated);
  };

  // Calculate live totals
  const totalAmount = items.reduce((sum, item) => {
    const prod = products.find((p) => p.id === item.product_id);
    if (!prod) return sum;
    return sum + Number(prod.price) * item.quantity;
  }, 0);

  const willRequireApproval = totalAmount > 1000;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!customerId) {
      setError('Please select a customer');
      return;
    }

    const invalidItem = items.find((i) => i.product_id === 0 || i.quantity <= 0);
    if (invalidItem) {
      setError('Please select a valid product and positive quantity for all line items');
      return;
    }

    setSubmitting(true);
    const result = await dispatch(
      createOrder({
        customer_id: Number(customerId),
        items: items.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
      })
    );
    setSubmitting(false);

    if (result.success) {
      navigate('/orders');
    } else {
      setError(result.error || 'Failed to place order');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back button */}
      <div>
        <Link
          to="/orders"
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-500 hover:text-slate-800 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to orders</span>
        </Link>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight mt-2">Create Sales Order</h2>
        <p className="text-sm text-slate-500">
          Reserve stock immediately with database concurrency protection
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 text-rose-700 rounded-lg border border-rose-200 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Threshold notification banner */}
      <div
        className={`p-4 rounded-xl border flex items-start gap-3 transition-colors ${
          willRequireApproval
            ? 'bg-amber-50 border-amber-200 text-amber-800'
            : 'bg-indigo-50/60 border-indigo-100 text-indigo-800'
        }`}
      >
        <Info className="w-5 h-5 shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <p className="font-semibold">
            {willRequireApproval
              ? 'Manager Approval Required (> $1,000.00)'
              : 'Direct Auto-Confirmation (≤ $1,000.00)'}
          </p>
          <p className="text-slate-600">
            {willRequireApproval
              ? 'This order total exceeds the $1,000 threshold. It will enter PENDING_APPROVAL and notify the Manager. Stock is safely reserved.'
              : 'This order will be immediately CONFIRMED upon creation and stock will be deducted.'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-6">
        {/* Customer Select */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
            Select Customer
          </label>
          <select
            required
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">-- Choose a customer --</option>
            {customers.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} {c.company_name ? `(${c.company_name})` : ''} - {c.email}
              </option>
            ))}
          </select>
        </div>

        {/* Line Items */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Order Items
            </label>
            <button
              type="button"
              onClick={handleAddItem}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-700 cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Line Item</span>
            </button>
          </div>

          <div className="space-y-2.5">
            {items.map((item, index) => {
              const selectedProd = products.find((p) => p.id === item.product_id);
              const subtotal = selectedProd ? Number(selectedProd.price) * item.quantity : 0;

              return (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-200 rounded-lg"
                >
                  {/* Product Picker */}
                  <div className="flex-1">
                    <select
                      value={item.product_id}
                      onChange={(e) =>
                        handleItemChange(index, 'product_id', Number(e.target.value))
                      }
                      className="w-full px-3 py-2 bg-white border border-slate-200 rounded-md text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value={0}>-- Select Product --</option>
                      {products.map((p) => (
                        <option key={p.id} value={p.id} disabled={p.stock_quantity <= 0}>
                          {p.name} (${Number(p.price).toFixed(2)}) - {p.stock_quantity} available
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Quantity */}
                  <div className="w-24">
                    <input
                      type="number"
                      min={1}
                      max={selectedProd ? selectedProd.stock_quantity : 9999}
                      value={item.quantity}
                      onChange={(e) =>
                        handleItemChange(index, 'quantity', parseInt(e.target.value, 10) || 1)
                      }
                      className="w-full px-3 py-2 bg-white border border-slate-200 rounded-md text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  {/* Subtotal */}
                  <div className="w-28 text-right font-mono font-medium text-slate-800 text-sm">
                    ${subtotal.toFixed(2)}
                  </div>

                  {/* Delete Item */}
                  <button
                    type="button"
                    onClick={() => handleRemoveItem(index)}
                    disabled={items.length === 1}
                    className="p-2 text-slate-400 hover:text-rose-600 rounded-md transition-colors disabled:opacity-30 cursor-pointer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Total & Submit */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 uppercase font-semibold">Grand Total:</span>
            <div className="text-2xl font-bold text-slate-900">${totalAmount.toFixed(2)}</div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors disabled:opacity-50 flex items-center gap-2 cursor-pointer"
          >
            {submitting ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <ShoppingCart className="w-4 h-4" />
                <span>Place Order</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
