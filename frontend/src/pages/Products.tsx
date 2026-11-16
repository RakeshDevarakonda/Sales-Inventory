import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import {
  fetchProducts,
  createProduct,
  updateProduct,
  toggleProductStatus,
  adjustStock,
} from '../store/slices/productSlice';
import { Modal, ConfirmDialog } from '../components/common/Modal';
import { Pagination } from '../components/common/Pagination';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  Package,
  Plus,
  AlertCircle,
  RefreshCw,
  SlidersHorizontal,
  Edit2,
  CheckCircle,
  XCircle,
  Search,
} from 'lucide-react';

export default function Products() {
  const dispatch = useAppDispatch();
  const { items: products, total, page, limit, totalPages, loading, error } = useAppSelector((state) => state.products);
  const { user } = useAppSelector((state) => state.auth);

  const [currentPage, setCurrentPage] = useState<number>(1);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);

  // New product form
  const [newName, setNewName] = useState('');
  const [newSku, setNewSku] = useState('');
  const [newPrice, setNewPrice] = useState('');
  const [newStock, setNewStock] = useState('0');
  const [newDesc, setNewDesc] = useState('');

  // Edit product form
  const [editName, setEditName] = useState('');
  const [editSku, setEditSku] = useState('');
  const [editPrice, setEditPrice] = useState('');
  const [editDesc, setEditDesc] = useState('');

  // Stock adjust form
  const [adjustQty, setAdjustQty] = useState('');
  const [actionError, setActionError] = useState<string | null>(null);

  // Status toggle confirmation dialog
  const [productToToggle, setProductToToggle] = useState<any>(null);
  const [toggling, setToggling] = useState(false);
  const [toggleError, setToggleError] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchProducts(false, currentPage, rowsPerPage));
  }, [dispatch, currentPage, rowsPerPage]);

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    const result = await dispatch(
      createProduct({
        name: newName,
        sku: newSku,
        price: parseFloat(newPrice),
        stock_quantity: parseInt(newStock, 10),
        description: newDesc || undefined,
      })
    );
    if (result.success) {
      setShowAddModal(false);
      setNewName('');
      setNewSku('');
      setNewPrice('');
      setNewStock('0');
      setNewDesc('');
    } else {
      setActionError(result.error || 'Failed to create product');
    }
  };

  const handleOpenEdit = (product: any) => {
    setSelectedProduct(product);
    setEditName(product.name);
    setEditSku(product.sku);
    setEditPrice(String(product.price));
    setEditDesc(product.description || '');
    setActionError(null);
    setShowEditModal(true);
  };

  const handleUpdateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (!selectedProduct) return;

    const result = await dispatch(
      updateProduct(selectedProduct.id, {
        name: editName,
        price: parseFloat(editPrice),
        description: editDesc || undefined,
      })
    );

    if (result.success) {
      setShowEditModal(false);
      setSelectedProduct(null);
    } else {
      setActionError(result.error || 'Failed to update product');
    }
  };

  const handleToggleStatus = (product: any) => {
    setToggleError(null);
    setProductToToggle(product);
  };

  const confirmToggleStatus = async () => {
    if (!productToToggle) return;
    setToggling(true);
    setToggleError(null);
    const res = await dispatch(toggleProductStatus(productToToggle.id, !productToToggle.is_active));
    setToggling(false);
    if (res.success) {
      setProductToToggle(null);
      setToggleError(null);
    } else {
      const errorMsg = res.error || 'Failed to toggle product status';
      setToggleError(errorMsg);
      setActionError(errorMsg);
    }
  };

  const handleAdjustStock = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (!selectedProduct) return;

    const change = parseInt(adjustQty, 10);
    if (isNaN(change)) return;

    const result = await dispatch(
      adjustStock({
        product_id: selectedProduct.id,
        change_quantity: change,
      })
    );

    if (result.success) {
      setShowAdjustModal(false);
      setSelectedProduct(null);
      setAdjustQty('');
    } else {
      setActionError(result.error || 'Stock adjustment failed');
    }
  };

  const filteredProducts = products.filter((p) => {
    const term = searchTerm.toLowerCase();
    return (
      p.name.toLowerCase().includes(term) ||
      p.sku.toLowerCase().includes(term) ||
      (p.description && p.description.toLowerCase().includes(term))
    );
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">Products & Inventory</h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Manage product catalog, prices, and stock allocations
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => dispatch(fetchProducts())}
            className="p-2 rounded-md bg-white border border-slate-300 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
            title="Refresh Catalog"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          {user?.role === 'MANAGER' && (
            <button
              onClick={() => {
                setActionError(null);
                setShowAddModal(true);
              }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium rounded-md shadow-2xs transition-colors cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Add Product</span>
            </button>
          )}
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
            placeholder="Search by product name, SKU, or details..."
            className="w-full pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-400 transition-colors"
          />
        </div>
      </div>

      {/* Products Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-semibold tracking-wider text-[11px]">
              <tr>
                <th className="px-6 py-3 w-16 text-center">S.No</th>
                <th className="px-6 py-3">Product Name</th>
                <th className="px-6 py-3">SKU</th>
                <th className="px-6 py-3">Unit Price</th>
                <th className="px-6 py-3">Stock Level</th>
                <th className="px-6 py-3">Status</th>
                {user?.role === 'MANAGER' && <th className="px-6 py-3 text-right">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12">
                    <LoadingSpinner message="Loading catalog items..." size="sm" />
                  </td>
                </tr>
              ) : filteredProducts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-slate-400 text-xs">
                    No products found matching your search.
                  </td>
                </tr>
              ) : (
                filteredProducts.map((product, idx) => {
                  const isLow = product.stock_quantity <= 10;
                  const serialNumber = (currentPage - 1) * rowsPerPage + idx + 1;
                  return (
                    <tr key={product.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-6 py-3.5 text-center font-mono text-slate-400 text-xs">
                        {serialNumber}
                      </td>
                      <td className="px-6 py-3.5">
                        <div className="font-semibold text-slate-900">{product.name}</div>
                        {product.description && (
                          <div className="text-[11px] text-slate-500 truncate max-w-sm mt-0.5">
                            {product.description}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-3.5 font-mono text-slate-600 font-medium">{product.sku}</td>
                      <td className="px-6 py-3.5 font-bold text-slate-900 font-mono">
                        ₹{Number(product.price).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td className="px-6 py-3.5">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border ${
                            isLow
                              ? 'bg-rose-50 text-rose-700 border-rose-200'
                              : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          }`}
                        >
                          {product.stock_quantity} in stock
                        </span>
                      </td>
                      <td className="px-6 py-3.5">
                        <button
                          type="button"
                          onClick={() => user?.role === 'MANAGER' && handleToggleStatus(product)}
                          disabled={user?.role !== 'MANAGER'}
                          title={user?.role === 'MANAGER' ? 'Click to toggle status' : undefined}
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium border transition-colors ${
                            user?.role === 'MANAGER' ? 'cursor-pointer hover:bg-slate-100' : 'cursor-default'
                          } ${
                            product.is_active
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                              : 'bg-slate-100 text-slate-600 border-slate-200'
                          }`}
                        >
                          {product.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                      {user?.role === 'MANAGER' && (
                        <td className="px-6 py-3.5 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleOpenEdit(product)}
                              className="px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded transition-colors cursor-pointer"
                              title="Edit product details & price"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => {
                                setSelectedProduct(product);
                                setAdjustQty('');
                                setActionError(null);
                                setShowAdjustModal(true);
                              }}
                              className="px-2.5 py-1 text-xs font-medium text-slate-900 bg-slate-100 hover:bg-slate-200 rounded transition-colors cursor-pointer"
                              title="Adjust stock"
                            >
                              Stock
                            </button>
                          </div>
                        </td>
                      )}
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

      {/* Add Product Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add Product"
        subtitle="Create a catalog entry with unit pricing and stock level"
        maxWidth="md"
      >
        {actionError && (
          <div className="mb-4 p-3 bg-rose-50 text-rose-700 text-xs rounded-lg border border-rose-200">
            {actionError}
          </div>
        )}

        <form onSubmit={handleCreateProduct} className="space-y-3.5">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Product Name</label>
            <input
              type="text"
              required
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="e.g. Ergonomic Office Chair"
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">SKU</label>
              <input
                type="text"
                required
                value={newSku}
                onChange={(e) => setNewSku(e.target.value)}
                placeholder="FUR-CHR-001"
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Unit Price (₹)</label>
              <input
                type="number"
                step="0.01"
                required
                value={newPrice}
                onChange={(e) => setNewPrice(e.target.value)}
                placeholder="249.99"
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Initial Stock</label>
            <input
              type="number"
              required
              value={newStock}
              onChange={(e) => setNewStock(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Description</label>
            <textarea
              rows={2}
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Optional product description..."
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
              Save Product
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Product Modal */}
      <Modal
        isOpen={showEditModal && Boolean(selectedProduct)}
        onClose={() => setShowEditModal(false)}
        title="Edit Product"
        subtitle="Update catalog details and price points"
        maxWidth="md"
      >
        {actionError && (
          <div className="mb-4 p-3 bg-rose-50 text-rose-700 text-xs rounded-lg border border-rose-200">
            {actionError}
          </div>
        )}

        <form onSubmit={handleUpdateProduct} className="space-y-3.5">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Name</label>
            <input
              type="text"
              required
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                SKU <span className="text-[10px] text-slate-400 font-normal">(Immutable)</span>
              </label>
              <input
                type="text"
                disabled
                value={editSku}
                className="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded text-xs text-slate-500 font-mono cursor-not-allowed select-none"
                title="Product SKU is a unique immutable identifier and cannot be modified."
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Price (₹)</label>
              <input
                type="number"
                step="0.01"
                required
                value={editPrice}
                onChange={(e) => setEditPrice(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Description</label>
            <textarea
              rows={2}
              value={editDesc}
              onChange={(e) => setEditDesc(e.target.value)}
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
              Update Product
            </button>
          </div>
        </form>
      </Modal>

      {/* Adjust Stock Modal */}
      <Modal
        isOpen={showAdjustModal && Boolean(selectedProduct)}
        onClose={() => setShowAdjustModal(false)}
        title="Adjust Inventory"
        subtitle={selectedProduct ? `${selectedProduct.name} • Current Stock: ${selectedProduct.stock_quantity}` : undefined}
        maxWidth="sm"
      >
        {actionError && (
          <div className="mb-4 p-3 bg-rose-50 text-rose-700 text-xs rounded-lg border border-rose-200">
            {actionError}
          </div>
        )}

        <form onSubmit={handleAdjustStock} className="space-y-3.5">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Quantity Adjustment (+ to add, - to deduct)
            </label>
            <input
              type="number"
              required
              value={adjustQty}
              onChange={(e) => setAdjustQty(e.target.value)}
              placeholder="e.g. 50 or -10"
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:border-slate-500"
            />
            <span className="text-[11px] text-slate-500 mt-1 block">
              Executed with database row locking to prevent concurrent overwrite.
            </span>
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setShowAdjustModal(false)}
              className="px-3.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-md transition-colors cursor-pointer border border-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors cursor-pointer shadow-2xs"
            >
              Apply Stock
            </button>
          </div>
        </form>
      </Modal>

      {/* Product Status Toggle Confirmation Dialog */}
      <ConfirmDialog
        isOpen={Boolean(productToToggle)}
        onClose={() => {
          setProductToToggle(null);
          setToggleError(null);
        }}
        onConfirm={confirmToggleStatus}
        title={productToToggle?.is_active ? 'Deactivate Product' : 'Activate Product'}
        message={
          productToToggle?.is_active
            ? `Are you sure you want to deactivate "${productToToggle?.name}"? Inactive items will be excluded from new sales orders until re-activated.`
            : `Are you sure you want to activate "${productToToggle?.name}"? It will become immediately available in the sales order catalog.`
        }
        confirmText={productToToggle?.is_active ? 'Deactivate' : 'Activate'}
        variant={productToToggle?.is_active ? 'warning' : 'primary'}
        loading={toggling}
        error={toggleError}
      />
    </div>
  );
}
