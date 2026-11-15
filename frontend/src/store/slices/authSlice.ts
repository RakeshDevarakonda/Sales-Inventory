import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import api from '../../api/client';
import { User } from '../../types';
import { AppDispatch } from '../index';
import { getErrorMessage } from '../../utils/errors';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  initializing: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  loading: false,
  initializing: true,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setInitializing: (state, action: PayloadAction<boolean>) => {
      state.initializing = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    loginSuccess: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
      state.loading = false;
      state.error = null;
    },
    logoutSuccess: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.loading = false;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    forceLogout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.error = 'Session expired. Please log in again.';
    },
  },
});

export const {
  setLoading,
  setInitializing,
  setError,
  loginSuccess,
  logoutSuccess,
  clearError,
  forceLogout,
} = authSlice.actions;

// Login: Backend sets HttpOnly access_token & refresh_token cookies; returns { message, user }
export const login = (credentials: { username_or_email: string; password: string }) => async (dispatch: AppDispatch) => {
  dispatch(setLoading(true));
  dispatch(setError(null));
  try {
    const response = await api.post('/auth/login', credentials);
    const { user } = response.data;
    dispatch(loginSuccess(user));
    return { success: true, user };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Login failed');
    dispatch(setError(msg));
    dispatch(setLoading(false));
    return { success: false, error: msg };
  }
};

export const register = (userData: { username: string; email: string; password: string; full_name: string }) => async (dispatch: AppDispatch) => {
  dispatch(setLoading(true));
  dispatch(setError(null));
  try {
    const response = await api.post('/auth/register', userData);
    dispatch(setLoading(false));
    return { success: true, data: response.data };
  } catch (err: any) {
    const msg = getErrorMessage(err, 'Registration failed');
    dispatch(setError(msg));
    dispatch(setLoading(false));
    return { success: false, error: msg };
  }
};

// CheckAuth: Restores user session via HttpOnly cookies using single-responsibility check
export const checkAuth = () => async (dispatch: AppDispatch) => {
  dispatch(setInitializing(true));
  try {
    // 1. Check if an active session exists via access_token cookie
    const meRes = await api.get('/auth/me');
    dispatch(loginSuccess(meRes.data));
  } catch {
    // 2. If access_token is expired or absent, attempt silent refresh via refresh_token cookie
    try {
      await api.post('/auth/refresh');
      const retryMe = await api.get('/auth/me');
      dispatch(loginSuccess(retryMe.data));
    } catch {
      // No active session or refresh expired
      dispatch(logoutSuccess());
    }
  } finally {
    dispatch(setInitializing(false));
  }
};

export const logout = () => async (dispatch: AppDispatch) => {
  try {
    await api.post('/auth/logout');
  } catch {
    // Ignored
  } finally {
    dispatch(logoutSuccess());
  }
};

export default authSlice.reducer;
