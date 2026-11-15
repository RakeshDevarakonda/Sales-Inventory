import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchDashboardSummary } from '../store/slices/dashboardSlice';
import {
  DollarSign,
  ShoppingCart,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const dispatch = useAppDispatch();
  const { summary, loading, error } = useAppSelector((state) => state.dashboard);
  const { user } = useAppSelector((state) => state.auth);

  useEffect(() => {
    dispatch(fetchDashboardSummary());
  }, [dispatch]);

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-rose-50 text-rose-700 rounded-lg border border-rose-200">
        Failed to load dashboard: {error}
      </div>
    );
  }

  const pendingCount = summary?.orders_by_status?.PENDING_APPROVAL || 0;
  const confirmedCount = summary?.orders_by_status?.CONFIRMED || 0;
  const approvedCount = summary?.orders_by_status?.APPROVED || 0;

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Executive Dashboard</h2>
          <p className="text-sm text-slate-500 mt-1">Real-time metrics, order throughput, and inventory alerts</p>
        </div>
        <Link
          to="/orders/new"
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors cursor-pointer"
        >
          <ShoppingCart className="w-4 h-4" />
          <span>New Sales Order</span>
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Revenue */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Revenue</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">
            ${Number(summary?.total_revenue || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <p className="text-xs text-slate-400 mt-1">From approved & confirmed orders</p>
        </div>

        {/* Total Orders */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Orders</span>
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <ShoppingCart className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{summary?.total_orders || 0}</div>
          <div className="flex items-center gap-2 text-xs text-slate-500 mt-1">
            <span className="text-emerald-600 font-semibold">{confirmedCount + approvedCount} Completed</span>
          </div>
        </div>

        {/* Pending Approval */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Pending Approval</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{pendingCount}</div>
          <p className="text-xs text-slate-400 mt-1">
            {user?.role === 'MANAGER' ? 'Requires your review (> $1,000)' : 'Awaiting manager approval'}
          </p>
        </div>

        {/* Low Stock Alerts */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Low Stock Items</span>
            <div className="p-2 bg-rose-50 text-rose-600 rounded-lg">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{summary?.low_stock_count || 0}</div>
          <Link to="/products" className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-700 font-medium mt-1">
            <span>View inventory</span>
            <ArrowUpRight className="w-3 h-3" />
          </Link>
        </div>
      </div>

      {/* Recent Orders Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-semibold text-slate-900 text-sm">Recent Orders</h3>
          <Link to="/orders" className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">
            View all orders →
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50/75 border-b border-slate-100 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3.5">Order #</th>
                <th className="px-6 py-3.5">Customer</th>
                <th className="px-6 py-3.5">Placed By</th>
                <th className="px-6 py-3.5">Total</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {summary?.recent_orders && summary.recent_orders.length > 0 ? (
                summary.recent_orders.map((order) => {
                  let badgeClass = 'bg-slate-100 text-slate-700 border-slate-200';
                  if (order.status === 'CONFIRMED' || order.status === 'APPROVED') {
                    badgeClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                  } else if (order.status === 'PENDING_APPROVAL') {
                    badgeClass = 'bg-amber-50 text-amber-700 border-amber-200';
                  } else if (order.status === 'REJECTED' || order.status === 'CANCELLED') {
                    badgeClass = 'bg-rose-50 text-rose-700 border-rose-200';
                  }

                  return (
                    <tr key={order.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 font-mono font-medium text-slate-900">{order.order_number}</td>
                      <td className="px-6 py-4 text-slate-700">{order.customer_name || `Customer #${order.customer_id}`}</td>
                      <td className="px-6 py-4 text-slate-500 text-xs">{order.created_by_username || 'User'}</td>
                      <td className="px-6 py-4 font-semibold text-slate-900">
                        ${Number(order.total_amount).toFixed(2)}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeClass}`}>
                          {order.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-400">
                        {new Date(order.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-400 text-xs">
                    No orders recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
