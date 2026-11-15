import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import api from '../../api/client';
import { Customer } from '../../types';
import { AppDispatch } from '../index';

interface CustomerState {
  items: Customer[];
  loading: boolean;
  error: string | null;
}

const initialState: CustomerState = {
  items: [],
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
    setCustomers: (state, action: PayloadAction<Customer[]>) => {
      state.items = action.payload;
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

export const fetchCustomers = () => async (dispatch: AppDispatch) => {
  dispatch(setLoading(true));
  dispatch(setError(null));
  try {
    const response = await api.get('/customers');
    dispatch(setCustomers(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to fetch customers';
    dispatch(setError(msg));
    return { success: false, error: msg };
  }
};

export const createCustomer = (
  customerData: { name: string; email: string; phone?: string; company_name?: string; address?: string }
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.post('/customers', customerData);
    dispatch(addCustomer(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to create customer';
    return { success: false, error: msg };
  }
};

export const updateCustomer = (
  id: number,
  customerData: { name?: string; email?: string; phone?: string; company_name?: string; address?: string }
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.patch(`/customers/${id}`, customerData);
    dispatch(updateCustomerInList(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to update customer';
    return { success: false, error: msg };
  }
};

export const deleteCustomer = (id: number) => async (dispatch: AppDispatch) => {
  try {
    await api.delete(`/customers/${id}`);
    dispatch(removeCustomerFromList(id));
    return { success: true, id };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to delete customer';
    return { success: false, error: msg };
  }
};

export default customerSlice.reducer;
