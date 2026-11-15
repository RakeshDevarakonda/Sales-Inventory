import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchDashboardSummary } from '../store/slices/dashboardSlice';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  DollarSign,
  ShoppingCart,
  Clock,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  RefreshCw,
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
      <div className="min-h-[60vh] flex items-center justify-center">
        <LoadingSpinner message="Fetching dashboard analytics & KPI metrics..." size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-rose-50 text-rose-800 rounded-lg border border-rose-200 text-xs flex items-center justify-between">
        <span>Failed to load dashboard data: {error}</span>
        <button
          onClick={() => dispatch(fetchDashboardSummary())}
          className="px-3 py-1 bg-white border border-rose-200 hover:bg-rose-100 rounded text-xs font-medium cursor-pointer"
        >
          Retry
        </button>
      </div>
    );
  }

  const pendingCount = summary?.pending_approvals_count ?? (summary?.orders_by_status?.PENDING_APPROVAL || 0);
  const confirmedCount = summary?.confirmed_orders_count ?? (summary?.orders_by_status?.CONFIRMED || 0);
  const approvedCount = summary?.approved_orders_count ?? (summary?.orders_by_status?.APPROVED || 0);
  const totalOrders = summary?.total_orders_count ?? (summary?.total_orders || 0);
  const lowStock = summary?.low_stock_products_count ?? (summary?.low_stock_count || 0);
  const totalRevenue = Number(summary?.total_revenue || 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">Dashboard</h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Overview of commercial performance, inventory alerts, and order volume
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => dispatch(fetchDashboardSummary())}
            className="p-2 rounded-md bg-white border border-slate-300 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
            title="Refresh Metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <Link
            to="/orders/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium rounded-md shadow-2xs transition-colors cursor-pointer"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Create Sales Order</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Revenue */}
        <div className="bg-white rounded-lg border border-slate-200 p-5 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Total Revenue</span>
            <DollarSign className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono tracking-tight">
            ₹{totalRevenue.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Confirmed & approved orders</p>
        </div>

        {/* Total Orders */}
        <div className="bg-white rounded-lg border border-slate-200 p-5 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Order Volume</span>
            <ShoppingCart className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono tracking-tight">
            {totalOrders}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            {confirmedCount + approvedCount} fulfilled orders
          </p>
        </div>

        {/* Pending Approvals */}
        <div className="bg-white rounded-lg border border-slate-200 p-5 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Pending Review</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono tracking-tight">
            {pendingCount}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            {user?.role === 'MANAGER' ? 'Manager review required (> ₹1,000)' : 'Awaiting approval'}
          </p>
        </div>

        {/* Low Stock Alerts */}
        <div className="bg-white rounded-lg border border-slate-200 p-5 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Low Stock Items</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono tracking-tight">
            {lowStock}
          </div>
          <Link
            to="/products"
            className="inline-flex items-center gap-1 text-[11px] text-indigo-600 hover:text-indigo-800 font-medium mt-1 transition-colors"
          >
            <span>Review catalog</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      </div>

      {/* Recent Orders Section */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-white">
          <div>
            <h3 className="font-semibold text-slate-900 text-sm">Recent Sales Orders</h3>
            <p className="text-xs text-slate-500">Latest transactions registered in the system</p>
          </div>
          <Link
            to="/orders"
            className="text-xs font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
          >
            View all orders →
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-semibold tracking-wider text-[11px]">
              <tr>
                <th className="px-6 py-3 w-16 text-center">S.No</th>
                <th className="px-6 py-3">Order Number</th>
                <th className="px-6 py-3">Customer</th>
                <th className="px-6 py-3">Sales Rep</th>
                <th className="px-6 py-3">Total Amount</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {summary?.recent_orders && summary.recent_orders.length > 0 ? (
                summary.recent_orders.map((order, idx) => {
                  let badge = 'bg-slate-100 text-slate-700 border-slate-200';
                  if (order.status === 'CONFIRMED' || order.status === 'APPROVED') {
                    badge = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                  } else if (order.status === 'PENDING_APPROVAL') {
                    badge = 'bg-amber-50 text-amber-700 border-amber-200';
                  } else if (order.status === 'REJECTED' || order.status === 'CANCELLED') {
                    badge = 'bg-rose-50 text-rose-700 border-rose-200';
                  }

                  return (
                    <tr key={order.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-6 py-3.5 text-center font-mono text-slate-400 text-xs">
                        {idx + 1}
                      </td>
                      <td className="px-6 py-3.5 font-mono font-medium text-slate-900">{order.order_number}</td>
                      <td className="px-6 py-3.5 font-medium text-slate-800">
                        {order.customer_name || `Customer #${order.customer_id}`}
                      </td>
                      <td className="px-6 py-3.5 text-slate-500">{order.created_by_username || 'Sales Rep'}</td>
                      <td className="px-6 py-3.5 font-bold text-slate-900 font-mono">
                        ₹{Number(order.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td className="px-6 py-3.5">
                        <span className={`inline-flex px-2 py-0.5 rounded text-[11px] font-medium border ${badge}`}>
                          {order.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-3.5 text-slate-500">
                        {new Date(order.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-400 text-xs">
                    No orders placed yet.
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
