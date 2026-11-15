import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import api from '../../api/client';
import { AppDispatch } from '../index';
import { getErrorMessage } from '../../utils/errors';

interface SettingsState {
  approvalThreshold: number;
  loading: boolean;
  error: string | null;
}

const initialState: SettingsState = {
  approvalThreshold: 1000,
  loading: false,
  error: null,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.loading = false;
    },
    setThreshold: (state, action: PayloadAction<number>) => {
      state.approvalThreshold = action.payload;
      state.loading = false;
      state.error = null;
    },
  },
});

export const { setLoading, setError, setThreshold } = settingsSlice.actions;

export const fetchApprovalThreshold = () => async (dispatch: AppDispatch) => {
  try {
    const response = await api.get('/settings/threshold');
    const val = Number(response.data.approval_threshold);
    dispatch(setThreshold(val));
    return { success: true, threshold: val };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to fetch approval threshold');
    dispatch(setError(msg));
    return { success: false, error: msg };
  }
};

export const updateApprovalThreshold = (newAmount: number) => async (dispatch: AppDispatch) => {
  dispatch(setLoading(true));
  try {
    const response = await api.patch('/settings/threshold', { approval_threshold: newAmount });
    const val = Number(response.data.approval_threshold);
    dispatch(setThreshold(val));
    return { success: true, threshold: val };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Failed to update approval threshold');
    dispatch(setError(msg));
    return { success: false, error: msg };
  }
};

export default settingsSlice.reducer;
