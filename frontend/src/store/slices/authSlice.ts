import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import api, { setAccessToken } from '../../api/client';
import { User } from '../../types';
import { AppDispatch } from '../index';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  initializing: boolean;
  error: string | null;
}

// Initial state purely in-memory: no localStorage usage
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
      setAccessToken(null);
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

// Login thunk: keeps access token in memory, refresh token in HttpOnly cookie
export const login = (credentials: { username_or_email: string; password: string }) => async (dispatch: AppDispatch) => {
  dispatch(setLoading(true));
  dispatch(setError(null));
  try {
    const response = await api.post('/auth/login', credentials);
    const { access_token, user } = response.data;
    setAccessToken(access_token);
    dispatch(loginSuccess(user));
    return { success: true, user };
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Login failed';
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
    const msg = err.response?.data?.detail || 'Registration failed';
    dispatch(setError(msg));
    dispatch(setLoading(false));
    return { success: false, error: msg };
  }
};

// CheckAuth: Uses the HttpOnly cookie at /auth/refresh to restore memory session on page load/reload
export const checkAuth = () => async (dispatch: AppDispatch) => {
  dispatch(setInitializing(true));
  try {
    const refreshRes = await api.post('/auth/refresh');
    const { access_token } = refreshRes.data;
    setAccessToken(access_token);

    const meRes = await api.get('/auth/me');
    dispatch(loginSuccess(meRes.data));
  } catch {
    setAccessToken(null);
    dispatch(logoutSuccess());
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
    setAccessToken(null);
    dispatch(logoutSuccess());
  }
};

export default authSlice.reducer;
