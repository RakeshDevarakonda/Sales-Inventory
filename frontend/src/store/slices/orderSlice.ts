import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import api from '../../api/client';
import { Order } from '../../types';
import { AppDispatch } from '../index';

interface OrderState {
  items: Order[];
  loading: boolean;
  error: string | null;
}

const initialState: OrderState = {
  items: [],
  loading: false,
  error: null,
};

const orderSlice = createSlice({
  name: 'orders',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.loading = false;
    },
    clearOrderError: (state) => {
      state.error = null;
    },
    setOrders: (state, action: PayloadAction<Order[]>) => {
      state.items = action.payload;
      state.loading = false;
      state.error = null;
    },
    addOrder: (state, action: PayloadAction<Order>) => {
      state.items.unshift(action.payload);
    },
    updateOrderInList: (state, action: PayloadAction<Order>) => {
      const index = state.items.findIndex((o) => o.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    },
    markCancelled: (state, action: PayloadAction<number>) => {
      const order = state.items.find((o) => o.id === action.payload);
      if (order) {
        order.status = 'CANCELLED';
      }
    },
  },
});

export const {
  setLoading,
  setError,
  clearOrderError,
  setOrders,
  addOrder,
  updateOrderInList,
  markCancelled,
} = orderSlice.actions;

// Thunks using standard reducers
export const fetchOrders = (statusFilter: string | null = null) => async (dispatch: AppDispatch) => {
  dispatch(setLoading(true));
  dispatch(setError(null));
  try {
    const url = statusFilter ? `/orders?status=${statusFilter}` : '/orders';
    const response = await api.get(url);
    dispatch(setOrders(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to fetch orders';
    dispatch(setError(msg));
    return { success: false, error: msg };
  }
};

export const createOrder = (
  orderData: { customer_id: number; items: Array<{ product_id: number; quantity: number }> }
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.post('/orders', orderData);
    dispatch(addOrder(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to place order';
    return { success: false, error: msg };
  }
};

export const approveOrder = (
  { id, notes }: { id: number; notes?: string }
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.post(`/orders/${id}/approve`, { approval_notes: notes });
    dispatch(updateOrderInList(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to approve order';
    return { success: false, error: msg };
  }
};

export const rejectOrder = (
  { id, notes }: { id: number; notes?: string }
) => async (dispatch: AppDispatch) => {
  try {
    const response = await api.post(`/orders/${id}/reject`, { approval_notes: notes });
    dispatch(updateOrderInList(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to reject order';
    return { success: false, error: msg };
  }
};

export const cancelOrder = (id: number) => async (dispatch: AppDispatch) => {
  try {
    await api.post(`/orders/${id}/cancel`);
    dispatch(markCancelled(id));
    return { success: true, id };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to cancel order';
    return { success: false, error: msg };
  }
};

export default orderSlice.reducer;
