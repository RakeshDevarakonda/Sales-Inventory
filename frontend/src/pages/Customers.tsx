import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchCustomers, createCustomer, updateCustomer, deleteCustomer } from '../store/slices/customerSlice';
import { Modal, ConfirmDialog } from '../components/common/Modal';
import { Pagination } from '../components/common/Pagination';
import {
  Users,
  Plus,
  Mail,
  Phone,
  Building2,
  Edit2,
  Trash2,
  MapPin,
  Search,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';

export default function Customers() {
  const dispatch = useAppDispatch();
  const { items: customers, total, page, pageSize, totalPages, loading, error } = useAppSelector((state) => state.customers);
  const { user } = useAppSelector((state) => state.auth);

  const [currentPage, setCurrentPage] = useState<number>(1);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [customerToDelete, setCustomerToDelete] = useState<any>(null);
  const [deleting, setDeleting] = useState(false);

  // Form fields
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchCustomers(currentPage, rowsPerPage));
  }, [dispatch, currentPage, rowsPerPage]);

  const handleCreateCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);

    if (!name.trim() || !email.trim() || !phone.trim() || !address.trim()) {
      setActionError('All fields (Full Name, Email, Phone, Address) are mandatory.');
      return;
    }

    const cleanPhone = phone.trim().replace(/\D/g, '');
    if (cleanPhone.length !== 10) {
      setActionError('Phone number must be exactly 10 digits.');
      return;
    }

    const result = await dispatch(
      createCustomer({
        name: name.trim(),
        email: email.trim(),
        phone: cleanPhone,
        address: address.trim(),
      })
    );

    if (result.success) {
      setShowAddModal(false);
      resetForm();
    } else {
      setActionError(result.error || 'Failed to create customer');
    }
  };

  const handleOpenEdit = (c: any) => {
    setSelectedCustomer(c);
    setName(c.name);
    setEmail(c.email);
    setPhone(c.phone || '');
    setAddress(c.address || '');
    setActionError(null);
    setShowEditModal(true);
  };

  const handleUpdateCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (!selectedCustomer) return;

    if (!name.trim() || !email.trim() || !phone.trim() || !address.trim()) {
      setActionError('All fields (Full Name, Email, Phone, Address) are mandatory.');
      return;
    }

    const cleanPhone = phone.trim().replace(/\D/g, '');
    if (cleanPhone.length !== 10) {
      setActionError('Phone number must be exactly 10 digits.');
      return;
    }

    const result = await dispatch(
      updateCustomer(selectedCustomer.id, {
        name: name.trim(),
        email: email.trim(),
        phone: cleanPhone,
        address: address.trim(),
      })
    );

    if (result.success) {
      setShowEditModal(false);
      setSelectedCustomer(null);
      resetForm();
    } else {
      setActionError(result.error || 'Failed to update customer');
    }
  };

  const handleDeleteCustomer = (c: any) => {
    setCustomerToDelete(c);
  };

  const confirmDeleteCustomer = async () => {
    if (!customerToDelete) return;
    setDeleting(true);
    const res = await dispatch(deleteCustomer(customerToDelete.id));
    setDeleting(false);
    if (res.success) {
      setCustomerToDelete(null);
    } else {
      setActionError(res.error || 'Failed to delete customer');
    }
  };

  const resetForm = () => {
    setName('');
    setEmail('');
    setPhone('');
    setAddress('');
  };

  const filteredCustomers = customers.filter((c) => {
    const term = searchTerm.toLowerCase();
    return (
      c.name.toLowerCase().includes(term) ||
      c.email.toLowerCase().includes(term) ||
      (c.phone && c.phone.toLowerCase().includes(term)) ||
      (c.address && c.address.toLowerCase().includes(term))
    );
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">Customer Directory</h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Manage corporate client accounts and contact persons
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => dispatch(fetchCustomers())}
            className="p-2 rounded-md bg-white border border-slate-300 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
            title="Refresh Directory"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => {
              resetForm();
              setActionError(null);
              setShowAddModal(true);
            }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium rounded-md shadow-2xs transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Add Customer</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 text-rose-800 rounded-lg border border-rose-200 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Filter / Search Bar */}
      <div className="flex items-center gap-3 bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by client name, company, email, or phone..."
            className="w-full pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-400 transition-colors"
          />
        </div>
      </div>

      {/* Customers Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-semibold tracking-wider text-[11px]">
              <tr>
                <th className="px-6 py-3 w-16 text-center">S.No</th>
                <th className="px-6 py-3">Customer Name</th>
                <th className="px-6 py-3">Email Address</th>
                <th className="px-6 py-3">Phone</th>
                <th className="px-6 py-3">Address</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading && customers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-400 text-xs">
                    Loading customer records...
                  </td>
                </tr>
              ) : filteredCustomers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-400 text-xs">
                    No customers found.
                  </td>
                </tr>
              ) : (
                filteredCustomers.map((c, idx) => {
                  const serialNumber = (currentPage - 1) * rowsPerPage + idx + 1;
                  return (
                    <tr key={c.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-6 py-3.5 text-center font-mono text-slate-400 text-xs">
                        {serialNumber}
                      </td>
                      <td className="px-6 py-3.5 font-semibold text-slate-900">{c.name}</td>
                      <td className="px-6 py-3.5 text-slate-600 font-mono text-[11px]">{c.email}</td>
                      <td className="px-6 py-3.5 text-slate-600">{c.phone || '—'}</td>
                      <td className="px-6 py-3.5 text-slate-500 max-w-sm truncate">
                        {c.address ? (
                          <div className="flex items-center gap-1">
                            <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                            <span className="truncate">{c.address}</span>
                          </div>
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="px-6 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => handleOpenEdit(c)}
                            className="px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded transition-colors cursor-pointer"
                            title="Edit Customer"
                          >
                            Edit
                          </button>
                          {user?.role === 'MANAGER' && (
                            <button
                              onClick={() => handleDeleteCustomer(c)}
                              className="px-2.5 py-1 text-xs font-medium text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded transition-colors cursor-pointer"
                              title="Delete Customer"
                            >
                              Delete
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

      {/* Add Customer Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add Customer"
        subtitle="Create a corporate account or client profile"
        maxWidth="md"
      >
        {actionError && (
          <div className="mb-4 p-3 bg-rose-50 text-rose-700 text-xs rounded-lg border border-rose-200">
            {actionError}
          </div>
        )}

        <form onSubmit={handleCreateCustomer} className="space-y-3.5">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Full Name <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Acme Corp or Jane Doe"
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Email Address <span className="text-rose-500">*</span>
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="contact@company.com"
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div className="grid grid-cols-1 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Phone (10 digits) <span className="text-rose-500">*</span>
              </label>
              <input
                type="tel"
                required
                maxLength={10}
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                placeholder="9876543210"
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Address <span className="text-rose-500">*</span>
            </label>
            <textarea
              rows={2}
              required
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="Full billing or delivery address..."
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setShowAddModal(false)}
              className="px-3.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-md transition-colors cursor-pointer border border-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors cursor-pointer shadow-2xs"
            >
              Save Customer
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Customer Modal */}
      <Modal
        isOpen={showEditModal && Boolean(selectedCustomer)}
        onClose={() => setShowEditModal(false)}
        title="Edit Customer"
        subtitle="Update contact details and address"
        maxWidth="md"
      >
        {actionError && (
          <div className="mb-4 p-3 bg-rose-50 text-rose-700 text-xs rounded-lg border border-rose-200">
            {actionError}
          </div>
        )}

        <form onSubmit={handleUpdateCustomer} className="space-y-3.5">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Full Name <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Email Address <span className="text-rose-500">*</span>
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div className="grid grid-cols-1 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Phone (10 digits) <span className="text-rose-500">*</span>
              </label>
              <input
                type="tel"
                required
                maxLength={10}
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                placeholder="9876543210"
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Address <span className="text-rose-500">*</span>
            </label>
            <textarea
              rows={2}
              required
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setShowEditModal(false)}
              className="px-3.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-md transition-colors cursor-pointer border border-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors cursor-pointer shadow-2xs"
            >
              Update Customer
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Customer Confirmation Dialog */}
      <ConfirmDialog
        isOpen={Boolean(customerToDelete)}
        onClose={() => setCustomerToDelete(null)}
        onConfirm={confirmDeleteCustomer}
        title="Delete Customer Profile"
        message={`Are you sure you want to delete "${customerToDelete?.name}"? All associated history will be impacted. This action cannot be reversed.`}
        confirmText="Delete Customer"
        variant="danger"
        loading={deleting}
      />
    </div>
  );
}
