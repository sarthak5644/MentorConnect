import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { User } from '@/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
}

const loadInitialState = (): AuthState => {
  try {
    const raw = localStorage.getItem('mc_auth');
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        user: parsed.user ?? null,
        accessToken: parsed.accessToken ?? null,
        refreshToken: parsed.refreshToken ?? null,
        isAuthenticated: !!parsed.accessToken,
      };
    }
  } catch {
    /* ignore corrupted storage */
  }
  return { user: null, accessToken: null, refreshToken: null, isAuthenticated: false };
};

const persist = (state: AuthState) => {
  localStorage.setItem(
    'mc_auth',
    JSON.stringify({ user: state.user, accessToken: state.accessToken, refreshToken: state.refreshToken })
  );
};

const authSlice = createSlice({
  name: 'auth',
  initialState: loadInitialState(),
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ user: User; accessToken: string; refreshToken: string }>
    ) => {
      state.user = action.payload.user;
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.isAuthenticated = true;
      persist(state);
    },
    setTokens: (state, action: PayloadAction<{ accessToken: string; refreshToken: string }>) => {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      persist(state);
    },
    updateUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      persist(state);
    },
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      localStorage.removeItem('mc_auth');
    },
  },
});

export const { setCredentials, setTokens, updateUser, logout } = authSlice.actions;
export default authSlice.reducer;