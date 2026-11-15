import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchOrders, approveOrder, rejectOrder, cancelOrder } from '../store/slices/orderSlice';
import { Modal, ConfirmDialog } from '../components/common/Modal';
import { Pagination } from '../components/common/Pagination';
import {
  ShoppingCart,
  Plus,
  CheckCircle,
  XCircle,
  Ban,
  Clock,
  Filter,
  Search,
  AlertCircle,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Orders() {
  const dispatch = useAppDispatch();
  const { items: orders, total, page, pageSize, totalPages, loading, error } = useAppSelector((state) => state.orders);
  const { user } = useAppSelector((state) => state.auth);

  const [statusFilter, setStatusFilter] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrder, setSelectedOrder] = useState<any>(null);
  const [approvalNotes, setApprovalNotes] = useState('');
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [orderToCancel, setOrderToCancel] = useState<number | null>(null);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    dispatch(fetchOrders(statusFilter || null, currentPage, rowsPerPage));
  }, [dispatch, statusFilter, currentPage, rowsPerPage]);

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

  const handleCancel = (orderId: number) => {
    setOrderToCancel(orderId);
  };

  const confirmCancelOrder = async () => {
    if (!orderToCancel) return;
    setCancelling(true);
    await dispatch(cancelOrder(orderToCancel));
    setCancelling(false);
    setOrderToCancel(null);
  };

  const filteredOrders = orders.filter((o) => {
    const term = searchTerm.toLowerCase();
    return (
      o.order_number.toLowerCase().includes(term) ||
      (o.customer_name && o.customer_name.toLowerCase().includes(term)) ||
      (o.created_by_username && o.created_by_username.toLowerCase().includes(term))
    );
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">Sales Orders</h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Orders exceeding ₹1,000 require manager approval before release
          </p>
        </div>

        <Link
          to="/orders/new"
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium rounded-md shadow-2xs transition-colors cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Create Sales Order</span>
        </Link>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 text-rose-800 rounded-lg border border-rose-200 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Filter / Search Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by order number, customer, or sales rep..."
            className="w-full pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-400 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-md text-xs w-full sm:w-auto">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent text-slate-700 font-medium focus:outline-none cursor-pointer w-full sm:w-auto"
            >
              <option value="">All Statuses</option>
              <option value="PENDING_APPROVAL">Pending Approval</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-semibold tracking-wider text-[11px]">
              <tr>
                <th className="px-6 py-3">Order Number</th>
                <th className="px-6 py-3">Customer</th>
                <th className="px-6 py-3">Items</th>
                <th className="px-6 py-3">Total Amount</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Sales Rep</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading && orders.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-slate-400 text-xs">
                    Loading orders...
                  </td>
                </tr>
              ) : filteredOrders.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-slate-400 text-xs">
                    No orders found.
                  </td>
                </tr>
              ) : (
                filteredOrders.map((order) => {
                  let badge = 'bg-slate-100 text-slate-700 border-slate-200';
                  if (order.status === 'CONFIRMED' || order.status === 'APPROVED') {
                    badge = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                  } else if (order.status === 'PENDING_APPROVAL') {
                    badge = 'bg-amber-50 text-amber-700 border-amber-200';
                  } else if (order.status === 'REJECTED' || order.status === 'CANCELLED') {
                    badge = 'bg-rose-50 text-rose-700 border-rose-200';
                  }

                  const isPending = order.status === 'PENDING_APPROVAL';
                  const canCancel =
                    ['PENDING_APPROVAL', 'CONFIRMED', 'APPROVED'].includes(order.status) &&
                    (user?.role === 'MANAGER' || order.created_by_id === user?.id);

                  return (
                    <tr key={order.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-6 py-3.5 font-mono font-medium text-slate-900">{order.order_number}</td>
                      <td className="px-6 py-3.5 font-medium text-slate-800">
                        {order.customer_name || `Customer #${order.customer_id}`}
                      </td>
                      <td className="px-6 py-3.5 text-slate-500">
                        {order.items?.length || 0} line item(s)
                      </td>
                      <td className="px-6 py-3.5 font-bold text-slate-900 font-mono">
                        ₹{Number(order.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td className="px-6 py-3.5">
                        <span className={`inline-flex px-2 py-0.5 rounded text-[11px] font-medium border ${badge}`}>
                          {order.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-3.5 text-slate-500">{order.created_by_username || 'Sales Rep'}</td>
                      <td className="px-6 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* Manager Controls for Pending */}
                          {user?.role === 'MANAGER' && isPending && (
                            <>
                              <button
                                onClick={() => {
                                  setSelectedOrder(order);
                                  setActionType('approve');
                                  setActionError(null);
                                }}
                                className="px-2.5 py-1 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded transition-colors cursor-pointer"
                                title="Approve order"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => {
                                  setSelectedOrder(order);
                                  setActionType('reject');
                                  setActionError(null);
                                }}
                                className="px-2.5 py-1 text-xs font-medium text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded transition-colors cursor-pointer"
                                title="Reject order"
                              >
                                Reject
                              </button>
                            </>
                          )}

                          {canCancel && (
                            <button
                              onClick={() => handleCancel(order.id)}
                              className="px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded transition-colors cursor-pointer"
                              title="Cancel order"
                            >
                              Cancel
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

        {/* Pagination Footer */}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          pageSize={rowsPerPage}
          totalItems={total}
          onPageChange={setCurrentPage}
          onPageSizeChange={setRowsPerPage}
          pageSizeOptions={[5, 10, 20, 50]}
        />
      </div>

      {/* Review Notes Modal */}
      <Modal
        isOpen={Boolean(selectedOrder && actionType)}
        onClose={() => {
          setSelectedOrder(null);
          setActionType(null);
        }}
        title={actionType === 'approve' ? 'Approve Sales Order' : 'Reject Sales Order'}
        subtitle={
          selectedOrder
            ? `Order #${selectedOrder.order_number} • Total ₹${Number(selectedOrder.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
            : undefined
        }
        maxWidth="md"
      >
        {actionError && (
          <div className="mb-4 p-3 bg-rose-50 text-rose-700 text-xs rounded-lg border border-rose-200">
            {actionError}
          </div>
        )}

        <form onSubmit={handleAction} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Manager Review Notes
            </label>
            <textarea
              rows={3}
              value={approvalNotes}
              onChange={(e) => setApprovalNotes(e.target.value)}
              placeholder="Optional feedback for the sales representative..."
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div className="flex justify-end gap-2.5 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => {
                setSelectedOrder(null);
                setActionType(null);
              }}
              className="px-3.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-md transition-colors cursor-pointer border border-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`px-4 py-1.5 text-xs font-semibold text-white rounded-md transition-colors cursor-pointer shadow-xs ${
                actionType === 'approve'
                  ? 'bg-emerald-600 hover:bg-emerald-700'
                  : 'bg-rose-600 hover:bg-rose-700'
              }`}
            >
              Confirm {actionType === 'approve' ? 'Approval' : 'Rejection'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Cancel Order Confirmation Dialog */}
      <ConfirmDialog
        isOpen={Boolean(orderToCancel)}
        onClose={() => setOrderToCancel(null)}
        onConfirm={confirmCancelOrder}
        title="Cancel Sales Order"
        message="Are you sure you want to cancel this order? The order status will change to CANCELLED and any reserved inventory will be automatically restored."
        confirmText="Cancel Order"
        variant="warning"
        loading={cancelling}
      />
    </div>
  );
}
