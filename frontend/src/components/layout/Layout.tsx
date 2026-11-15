import React, { useEffect, useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { logout } from '../../store/slices/authSlice';
import { fetchApprovalThreshold, updateApprovalThreshold } from '../../store/slices/settingsSlice';
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Users,
  LogOut,
  Shield,
  UserCheck,
  Menu,
  X,
  Edit2,
  Check,
} from 'lucide-react';

export default function Layout() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const { approvalThreshold } = useAppSelector((state) => state.settings);

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [editingLimit, setEditingLimit] = useState(false);
  const [limitInput, setLimitInput] = useState('');

  useEffect(() => {
    dispatch(fetchApprovalThreshold());
  }, [dispatch]);

  const handleLogout = async () => {
    await dispatch(logout());
    navigate('/login');
  };

  const handleSaveLimit = async () => {
    const parsed = parseFloat(limitInput);
    if (!isNaN(parsed) && parsed > 0) {
      await dispatch(updateApprovalThreshold(parsed));
      setEditingLimit(false);
    }
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Orders', path: '/orders', icon: ShoppingCart },
    { name: 'Products & Inventory', path: '/products', icon: Package },
    { name: 'Customers', path: '/customers', icon: Users },
  ];

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col md:flex-row antialiased font-sans">
      {/* Mobile Topbar */}
      <header className="md:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-md bg-slate-900 flex items-center justify-center text-white font-bold text-sm">
            SI
          </div>
          <div>
            <h1 className="font-bold text-sm text-slate-900 tracking-tight leading-none">SalesInventory</h1>
            <p className="text-[11px] text-slate-500 mt-0.5">Enterprise Portal</p>
          </div>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 text-slate-600 hover:text-slate-900 rounded-md hover:bg-slate-100 transition-colors"
          aria-label="Toggle Navigation"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </header>

      {/* Mobile Drawer Backdrop */}
      {mobileMenuOpen && (
        <div
          className="md:hidden fixed inset-0 z-30 bg-slate-900/40 backdrop-blur-xs"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar (Clean Classic Navy / Slate) */}
      <aside
        className={`fixed md:sticky top-0 h-screen z-40 md:z-auto w-64 bg-[#0f172a] text-slate-300 flex flex-col justify-between transition-transform duration-200 ease-in-out shrink-0 ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Brand Header */}
          <div className="h-16 border-b border-slate-800/80 px-6 hidden md:flex items-center gap-3">
            <div className="w-8 h-8 rounded-md bg-white flex items-center justify-center text-slate-900 font-extrabold text-sm tracking-tight shadow-xs">
              SI
            </div>
            <div>
              <h1 className="font-semibold text-sm text-white tracking-tight">SalesInventory</h1>
              <p className="text-[11px] text-slate-400">Enterprise Edition</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1 flex-1 overflow-y-auto">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-3 py-2">
              Platform Overview
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-slate-800 text-white font-semibold'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0 text-slate-400" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* User Account / Footer */}
          <div className="p-3 border-t border-slate-800/80 bg-[#090d16]">
            <div className="flex items-center gap-2.5 px-2.5 py-2 mb-2">
              <div className="w-8 h-8 rounded-md bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-semibold text-slate-200 shrink-0">
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="truncate flex-1">
                <p className="text-xs font-medium text-slate-200 truncate">{user?.username}</p>
                <div className="flex items-center gap-1 mt-0.5">
                  {user?.role === 'MANAGER' ? (
                    <span className="inline-flex items-center gap-1 text-[10px] font-medium text-emerald-400">
                      <Shield className="w-3 h-3" />
                      Manager
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[10px] font-medium text-blue-400">
                      <UserCheck className="w-3 h-3" />
                      Sales Rep
                    </span>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-rose-400 hover:bg-slate-800/60 rounded-md transition-colors cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-[#f8fafc]">
        {/* Top Header Bar */}
        <header className="h-16 hidden md:flex items-center justify-between px-8 bg-white border-b border-slate-200 sticky top-0 z-20 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">
            Account: <strong className="text-slate-800 font-semibold">{user?.full_name || user?.username}</strong>
            <span className="mx-2 text-slate-300">|</span>
            Role: <span className="font-medium text-slate-700">{user?.role}</span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-md text-slate-600">
              <span className="text-slate-400">Approval Limit:</span>
              {editingLimit && user?.role === 'MANAGER' ? (
                <div className="flex items-center gap-1.5">
                  <input
                    type="number"
                    min={1}
                    value={limitInput}
                    onChange={(e) => setLimitInput(e.target.value)}
                    placeholder="1000"
                    className="w-20 px-1.5 py-0.5 bg-white border border-slate-300 rounded text-xs font-mono text-slate-900 focus:outline-none focus:border-slate-500"
                    autoFocus
                  />
                  <button
                    onClick={handleSaveLimit}
                    className="p-1 text-emerald-600 hover:text-emerald-700 cursor-pointer"
                    title="Save"
                  >
                    <Check className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setEditingLimit(false)}
                    className="p-1 text-slate-400 hover:text-slate-600 cursor-pointer"
                    title="Cancel"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-1.5">
                  <strong className="text-slate-800 font-mono">
                    ₹{Number(approvalThreshold || 1000).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </strong>
                  {user?.role === 'MANAGER' && (
                    <button
                      onClick={() => {
                        setLimitInput(String(approvalThreshold || 1000));
                        setEditingLimit(true);
                      }}
                      className="p-0.5 text-slate-400 hover:text-slate-700 transition-colors cursor-pointer"
                      title="Change approval threshold"
                    >
                      <Edit2 className="w-3 h-3" />
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content Body */}
        <div className="p-6 md:p-8 flex-1 overflow-x-hidden">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
