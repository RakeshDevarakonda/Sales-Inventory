import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import api from '../../api/client';
import { DashboardSummary } from '../../types';
import { AppDispatch } from '../index';

interface DashboardState {
  summary: DashboardSummary | null;
  loading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  summary: null,
  loading: false,
  error: null,
};

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.loading = false;
    },
    setSummary: (state, action: PayloadAction<DashboardSummary>) => {
      state.summary = action.payload;
      state.loading = false;
      state.error = null;
    },
  },
});

export const { setLoading, setError, setSummary } = dashboardSlice.actions;

export const fetchDashboardSummary = () => async (dispatch: AppDispatch) => {
  dispatch(setLoading(true));
  dispatch(setError(null));
  try {
    const response = await api.get('/dashboard/summary');
    dispatch(setSummary(response.data));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to load dashboard';
    dispatch(setError(msg));
    return { success: false, error: msg };
  }
};

export default dashboardSlice.reducer;
