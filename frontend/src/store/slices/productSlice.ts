import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import api from '../../api/client';
import { Product, StockAdjustment } from '../../types';
import { AppDispatch } from '../index';
import { getErrorMessage } from '../../utils/errors';

interface ProductState {
  items: Product[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  loading: boolean;
  error: string | null;
}

const initialState: ProductState = {
  items: [],
  total: 0,
  page: 1,
  limit: 10,
  totalPages: 1,
  loading: false,
  error: null,
};

const productSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.loading = false;
    },
    clearProductError: (state) => {
      state.error = null;
    },
    setProducts: (state, action: PayloadAction<Product[] | { items: Product[]; total: number; page: number; limit: number; total_pages: number }>) => {
      if (Array.isArray(action.payload)) {
        state.items = action.payload;
        state.total = action.payload.length;
        state.totalPages = 1;
      } else {
        state.items = action.payload.items;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.limit = action.payload.limit;
        state.totalPages = action.payload.total_pages;
      }
      state.loading = false;
      state.error = null;
    },
    addProduct: (state, action: PayloadAction<Product>) => {
      state.items.unshift(action.payload);
    },
    updateProductInList: (state, action: PayloadAction<Product>) => {
      const index = state.items.findIndex((p) => p.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    },
    updateProductStock: (state, action: PayloadAction<StockAdjustment>) => {
      const product = state.items.find((p) => p.id === action.payload.product_id);
      if (product) {
        product.stock_quantity = action.payload.new_stock;
      }
    },
  },
});

export const {
  setLoading,
  setError,
  clearProductError,
  setProducts,
  addProduct,
  updateProductInList,
  updateProductStock,
} = productSlice.actions;

// Fetch all products
export const fetchProducts = (
  activeOnly: boolean = false,
  page?: number,
  limit?: number
) => async (dispatch: AppDispatch) => {
  dispatch(setLoading(true));
  dispatch(setError(null));
  try {
    const params = new URLSearchParams();
    if (activeOnly) params.append('active_only', 'true');
    if (page) params.append('page', String(page));
    if (limit) params.append('limit', String(limit));

    const queryStr = params.toString();
    const url = queryStr ? `/products?${queryStr}` : '/products';
    const response = await api.get(url);
    dispatch(setProducts(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to fetch products');
    dispatch(setError(msg));
    return { success: false, error: msg };
  }
};

// Create product (Manager only)
export const createProduct = (
  productData: { name: string; sku: string; price: number; stock_quantity: number; description?: string }
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.post('/products', productData);
    dispatch(addProduct(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to create product');
    return { success: false, error: msg };
  }
};

// Full edit product (name, price, sku, description)
export const updateProduct = (
  id: number,
  data: Partial<Product>
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.patch(`/products/${id}`, data);
    dispatch(updateProductInList(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to update product');
    return { success: false, error: msg };
  }
};

// Toggle active/inactive status
export const toggleProductStatus = (
  id: number,
  is_active: boolean
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.patch(`/products/${id}/status`, { is_active });
    dispatch(updateProductInList(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to toggle product status');
    return { success: false, error: msg };
  }
};

// Adjust stock via /inventory/adjustments
export const adjustStock = (
  adjustmentData: { product_id: number; change_quantity: number }
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.post('/inventory/adjustments', adjustmentData);
    dispatch(updateProductStock(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to adjust stock');
    return { success: false, error: msg };
  }
};

export default productSlice.reducer;
