import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchCustomers } from '../store/slices/customerSlice';
import { fetchProducts } from '../store/slices/productSlice';
import { createOrder } from '../store/slices/orderSlice';
import { fetchApprovalThreshold } from '../store/slices/settingsSlice';
import {
  ShoppingCart,
  Plus,
  Trash2,
  ArrowLeft,
  AlertCircle,
  Info,
} from 'lucide-react';
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
  const { user } = useAppSelector((state) => state.auth);
  const { approvalThreshold } = useAppSelector((state) => state.settings);

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

  // Live subtotal calculation
  const totalAmount = items.reduce((sum, item) => {
    const prod = products.find((p) => p.id === item.product_id);
    if (!prod) return sum;
    return sum + Number(prod.price) * item.quantity;
  }, 0);

  const isManager = user?.role === 'MANAGER';
  const thresholdLimit = approvalThreshold || 1000;
  const willRequireApproval = totalAmount > thresholdLimit && !isManager;
  const formattedThreshold = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
  }).format(thresholdLimit);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!customerId) {
      setError('Please select a customer for this order');
      return;
    }

    const invalidItem = items.find((i) => i.product_id === 0 || i.quantity <= 0);
    if (invalidItem) {
      setError('Please select a valid product and positive quantity for each line item');
      return;
    }

    // Check for duplicate products across line items
    const selectedProductIds = items.map((i) => i.product_id);
    const uniqueProductIds = new Set(selectedProductIds);
    if (selectedProductIds.length !== uniqueProductIds.size) {
      setError('Duplicate products detected. Please adjust the quantity on a single line item rather than adding the same product multiple times.');
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
      {/* Back button & Heading */}
      <div>
        <Link
          to="/orders"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-slate-800 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to orders</span>
        </Link>
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 mt-2">Create Sales Order</h2>
        <p className="text-xs sm:text-sm text-slate-500">
          Stock is immediately deducted and reserved with transactional row-level protection
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 text-rose-800 rounded-lg border border-rose-200 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Threshold Information Card */}
      <div
        className={`p-4 rounded-lg border text-xs flex items-start gap-3 ${
          willRequireApproval
            ? 'bg-amber-50 border-amber-200 text-amber-900'
            : 'bg-slate-50 border-slate-200 text-slate-700'
        }`}
      >
        <Info className={`w-4 h-4 shrink-0 mt-0.5 ${willRequireApproval ? 'text-amber-600' : 'text-slate-500'}`} />
        <div className="space-y-0.5">
          <p className="font-semibold">
            {isManager
              ? 'Manager Direct Creation (Instant Confirmation)'
              : willRequireApproval
              ? `Manager Approval Workflow Triggered (> ${formattedThreshold})`
              : `Direct Auto-Confirmation (≤ ${formattedThreshold})`}
          </p>
          <p className={willRequireApproval ? 'text-amber-800' : 'text-slate-600'}>
            {isManager
              ? 'As a Manager, your sales orders are immediately CONFIRMED upon placement without requiring external review.'
              : willRequireApproval
              ? `This order total exceeds ${formattedThreshold}. It will enter PENDING_APPROVAL and notify management via email. Stock is safely reserved in the database.`
              : 'This order total is within the pre-approved threshold and will be marked as CONFIRMED upon submission.'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-lg p-6 shadow-2xs space-y-6">
        {/* Customer Select */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1.5">
            Select Customer
          </label>
          <select
            required
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
          >
            <option value="">-- Choose Customer Account --</option>
            {customers.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} — {c.email}
              </option>
            ))}
          </select>
        </div>

        {/* Line Items */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="block text-xs font-semibold text-slate-700">
              Line Items
            </label>
            <button
              type="button"
              onClick={handleAddItem}
              className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Item</span>
            </button>
          </div>

          <div className="space-y-2.5">
            {items.map((item, index) => {
              const selectedProd = products.find((p) => p.id === item.product_id);
              const subtotal = selectedProd ? Number(selectedProd.price) * item.quantity : 0;

              return (
                <div
                  key={index}
                  className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 p-3 bg-slate-50 border border-slate-200 rounded"
                >
                  {/* Product Picker */}
                  <div className="flex-1">
                    <select
                      value={item.product_id}
                      onChange={(e) =>
                        handleItemChange(index, 'product_id', Number(e.target.value))
                      }
                      className="w-full px-3 py-1.5 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
                    >
                      <option value={0}>-- Select Product --</option>
                      {products.map((p) => {
                        const isAlreadyChosen = items.some(
                          (otherItem, otherIdx) => otherIdx !== index && otherItem.product_id === p.id
                        );
                        return (
                          <option
                            key={p.id}
                            value={p.id}
                            disabled={p.stock_quantity <= 0 || isAlreadyChosen}
                          >
                            {p.name} (₹{Number(p.price).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}) — {p.stock_quantity} in stock {isAlreadyChosen ? '(already added)' : ''}
                          </option>
                        );
                      })}
                    </select>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-3">
                    {/* Quantity */}
                    <div className="w-20">
                      <input
                        type="number"
                        min={1}
                        max={selectedProd ? selectedProd.stock_quantity : 9999}
                        value={item.quantity}
                        onChange={(e) =>
                          handleItemChange(index, 'quantity', parseInt(e.target.value, 10) || 1)
                        }
                        className="w-full px-2 py-1.5 bg-white border border-slate-300 rounded text-xs text-center text-slate-900 focus:outline-none focus:border-slate-500 font-mono"
                      />
                    </div>

                    {/* Subtotal */}
                    <div className="w-24 text-right font-mono font-bold text-slate-800 text-xs">
                      ₹{subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </div>

                    {/* Delete Item */}
                    <button
                      type="button"
                      onClick={() => handleRemoveItem(index)}
                      disabled={items.length === 1}
                      className="p-1.5 text-slate-400 hover:text-rose-600 rounded transition-colors disabled:opacity-20 cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer & Submit */}
        <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <span className="text-[11px] text-slate-500 uppercase font-semibold">Total Order Value:</span>
            <div className="text-2xl font-bold text-slate-900 font-mono mt-0.5">₹{totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full sm:w-auto px-6 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded transition-colors disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer shadow-2xs"
          >
            {submitting ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <ShoppingCart className="w-4 h-4" />
                <span>Submit Sales Order</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
