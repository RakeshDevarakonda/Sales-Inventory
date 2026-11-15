import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchOrders, approveOrder, rejectOrder, cancelOrder } from '../store/slices/orderSlice';
import { ShoppingCart, Plus, CheckCircle, XCircle, Ban, Clock, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Orders() {
  const dispatch = useAppDispatch();
  const { items: orders, loading, error } = useAppSelector((state) => state.orders);
  const { user } = useAppSelector((state) => state.auth);

  const [statusFilter, setStatusFilter] = useState<string>('');
  const [selectedOrder, setSelectedOrder] = useState<any>(null);
  const [approvalNotes, setApprovalNotes] = useState('');
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchOrders(statusFilter || null));
  }, [dispatch, statusFilter]);

  const handleAction = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (!selectedOrder || !actionType) return;

    let res;
    if (actionType === 'approve') {
      res = await dispatch(approveOrder({ id: selectedOrder.id, notes: approvalNotes }));
    } else {
      res = await dispatch(rejectOrder({ id: selectedOrder.id, notes: approvalNotes }));
    }

    if (res.success) {
      setSelectedOrder(null);
      setActionType(null);
      setApprovalNotes('');
    } else {
      setActionError(res.error || 'Action failed');
    }
  };

  const handleCancel = async (orderId: number) => {
    if (window.confirm('Are you sure you want to cancel this order? Reserved stock will be returned.')) {
      await dispatch(cancelOrder(orderId));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Sales Orders</h2>
          <p className="text-sm text-slate-500 mt-1">
            Orders exceeding $1,000 require manager approval before fulfillment
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Status filter */}
          <div className="flex items-center gap-2 bg-white px-3 py-2 border border-slate-200 rounded-lg text-sm shadow-xs">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent text-slate-700 text-xs font-medium focus:outline-none cursor-pointer"
            >
              <option value="">All Statuses</option>
              <option value="PENDING_APPROVAL">Pending Approval</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>

          <Link
            to="/orders/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Create Order</span>
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 text-rose-700 rounded-lg border border-rose-200 text-sm">
          {error}
        </div>
      )}

      {/* Orders Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-100 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3.5">Order #</th>
                <th className="px-6 py-3.5">Customer</th>
                <th className="px-6 py-3.5">Items</th>
                <th className="px-6 py-3.5">Total Amount</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">Placed By</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading && orders.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400 text-xs">
                    Loading orders...
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400 text-xs">
                    No orders match your filter.
                  </td>
                </tr>
              ) : (
                orders.map((order) => {
                  let badgeClass = 'bg-slate-100 text-slate-700 border-slate-200';
                  if (order.status === 'CONFIRMED' || order.status === 'APPROVED') {
                    badgeClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                  } else if (order.status === 'PENDING_APPROVAL') {
                    badgeClass = 'bg-amber-50 text-amber-700 border-amber-200';
                  } else if (order.status === 'REJECTED' || order.status === 'CANCELLED') {
                    badgeClass = 'bg-rose-50 text-rose-700 border-rose-200';
                  }

                  const isPending = order.status === 'PENDING_APPROVAL';
                  const canCancel =
                    ['PENDING_APPROVAL', 'CONFIRMED', 'APPROVED'].includes(order.status) &&
                    (user?.role === 'MANAGER' || order.created_by_id === user?.id);

                  return (
                    <tr key={order.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 font-mono font-medium text-slate-900">{order.order_number}</td>
                      <td className="px-6 py-4 text-slate-700 font-medium">
                        {order.customer_name || `Customer #${order.customer_id}`}
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-500">
                        {order.items?.length || 0} line item(s)
                      </td>
                      <td className="px-6 py-4 font-semibold text-slate-900">
                        ${Number(order.total_amount).toFixed(2)}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeClass}`}>
                          {order.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-500">{order.created_by_username || 'User'}</td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {/* Manager Review Buttons for Pending Orders */}
                          {user?.role === 'MANAGER' && isPending && (
                            <>
                              <button
                                onClick={() => {
                                  setSelectedOrder(order);
                                  setActionType('approve');
                                  setActionError(null);
                                }}
                                className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-md border border-emerald-200 transition-colors cursor-pointer"
                                title="Approve Order"
                              >
                                <CheckCircle className="w-3.5 h-3.5" />
                                <span>Approve</span>
                              </button>
                              <button
                                onClick={() => {
                                  setSelectedOrder(order);
                                  setActionType('reject');
                                  setActionError(null);
                                }}
                                className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-md border border-rose-200 transition-colors cursor-pointer"
                                title="Reject Order"
                              >
                                <XCircle className="w-3.5 h-3.5" />
                                <span>Reject</span>
                              </button>
                            </>
                          )}

                          {canCancel && (
                            <button
                              onClick={() => handleCancel(order.id)}
                              className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-md transition-colors cursor-pointer"
                              title="Cancel Order"
                            >
                              <Ban className="w-3.5 h-3.5" />
                              <span>Cancel</span>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Approve / Reject Modal */}
      {selectedOrder && actionType && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-900 mb-1">
              {actionType === 'approve' ? 'Approve Order' : 'Reject Order'}
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Order <strong>{selectedOrder.order_number}</strong> (${Number(selectedOrder.total_amount).toFixed(2)})
            </p>

            {actionError && (
              <div className="mb-4 p-3 bg-rose-50 text-rose-700 text-xs rounded-lg border border-rose-200">
                {actionError}
              </div>
            )}

            <form onSubmit={handleAction} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Manager Review Notes
                </label>
                <textarea
                  rows={3}
                  value={approvalNotes}
                  onChange={(e) => setApprovalNotes(e.target.value)}
                  placeholder="Optional review feedback sent to sales rep..."
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedOrder(null);
                    setActionType(null);
                  }}
                  className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className={`px-4 py-2 text-xs font-medium text-white rounded-lg transition-colors shadow-xs cursor-pointer ${
                    actionType === 'approve'
                      ? 'bg-emerald-600 hover:bg-emerald-700'
                      : 'bg-rose-600 hover:bg-rose-700'
                  }`}
                >
                  Confirm {actionType === 'approve' ? 'Approval' : 'Rejection'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
