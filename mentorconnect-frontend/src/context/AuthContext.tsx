import { createContext, useContext, useCallback, ReactNode } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { setCredentials, logout as logoutAction, updateUser } from '@/store/authSlice';
import { authApi } from '@/api/endpoints';
import { LoginRequest, RegisterRequest, User, RoleName } from '@/types';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  role: RoleName | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((s) => s.auth);

  const login = useCallback(
    async (data: LoginRequest) => {
      const res = await authApi.login(data);
      dispatch(
        setCredentials({
          user: res.user,
          accessToken: res.access_token,
          refreshToken: res.refresh_token,
        })
      );
    },
    [dispatch]
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      const res = await authApi.register(data);
      dispatch(
        setCredentials({
          user: res.user,
          accessToken: res.access_token,
          refreshToken: res.refresh_token,
        })
      );
    },
    [dispatch]
  );

  const logout = useCallback(() => {
    authApi.logout().catch(() => void 0);
    dispatch(logoutAction());
  }, [dispatch]);

  const refreshUser = useCallback(
    (u: User) => {
      dispatch(updateUser(u));
    },
    [dispatch]
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        role: user?.role.name ?? null,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}