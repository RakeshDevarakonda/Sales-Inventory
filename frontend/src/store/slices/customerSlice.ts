import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import api from '../../api/client';
import { Customer } from '../../types';
import { AppDispatch } from '../index';
import { getErrorMessage } from '../../utils/errors';

interface CustomerState {
  items: Customer[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  loading: boolean;
  error: string | null;
}

const initialState: CustomerState = {
  items: [],
  total: 0,
  page: 1,
  limit: 10,
  totalPages: 1,
  loading: false,
  error: null,
};

const customerSlice = createSlice({
  name: 'customers',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.loading = false;
    },
    setCustomers: (state, action: PayloadAction<Customer[] | { items: Customer[]; total: number; page: number; limit: number; total_pages: number }>) => {
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
    addCustomer: (state, action: PayloadAction<Customer>) => {
      state.items.unshift(action.payload);
    },
    updateCustomerInList: (state, action: PayloadAction<Customer>) => {
      const index = state.items.findIndex((c) => c.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    },
    removeCustomerFromList: (state, action: PayloadAction<number>) => {
      state.items = state.items.filter((c) => c.id !== action.payload);
    },
  },
});

export const {
  setLoading,
  setError,
  setCustomers,
  addCustomer,
  updateCustomerInList,
  removeCustomerFromList,
} = customerSlice.actions;

export const fetchCustomers = (page?: number, limit?: number) => async (dispatch: AppDispatch) => {
  dispatch(setLoading(true));
  dispatch(setError(null));
  try {
    const params = new URLSearchParams();
    if (page) params.append('page', String(page));
    if (limit) params.append('limit', String(limit));

    const queryStr = params.toString();
    const url = queryStr ? `/customers?${queryStr}` : '/customers';
    const response = await api.get(url);
    dispatch(setCustomers(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to fetch customers');
    dispatch(setError(msg));
    return { success: false, error: msg };
  }
};

export const createCustomer = (
  customerData: { name: string; email: string; phone: string; address: string }
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.post('/customers', customerData);
    dispatch(addCustomer(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to create customer');
    return { success: false, error: msg };
  }
};

export const updateCustomer = (
  id: number,
  customerData: { name: string; email: string; phone: string; address: string }
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.patch(`/customers/${id}`, customerData);
    dispatch(updateCustomerInList(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to update customer');
    return { success: false, error: msg };
  }
};

export const deleteCustomer = (id: number) => async (dispatch: AppDispatch) => {
  try {
    await api.delete(`/customers/${id}`);
    dispatch(removeCustomerFromList(id));
    return { success: true, id };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to delete customer');
    return { success: false, error: msg };
  }
};

export default customerSlice.reducer;
