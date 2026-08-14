import { createContext, useContext, useCallback, ReactNode } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { setCredentials, logout as logoutAction, updateUser } from '@/store/authSlice';
import { authApi } from '@/api/endpoints';
import { LoginRequest, StudentRegisterRequest, MentorRegisterRequest, User, RoleName } from '@/types';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  role: RoleName | null;
  login: (data: LoginRequest) => Promise<User>;
  // Registration does NOT log the account in — the backend only returns the
  // created user, no tokens. OTP verification requires being logged in, so
  // the real flow is register -> login -> verify (accounts can log in while
  // status is "pending").
  registerStudent: (data: StudentRegisterRequest) => Promise<User>;
  registerMentor: (data: MentorRegisterRequest) => Promise<User>;
  logout: () => void;
  refreshUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, refreshToken } = useAppSelector((s) => s.auth);

  const login = useCallback(
    async (data: LoginRequest) => {
      const res = await authApi.login(data);
      dispatch(
        setCredentials({
          user: res.user,
          accessToken: res.tokens.access_token,
          refreshToken: res.tokens.refresh_token,
        })
      );
      return res.user;
    },
    [dispatch]
  );

  const registerStudent = useCallback((data: StudentRegisterRequest) => authApi.registerStudent(data), []);
  const registerMentor = useCallback((data: MentorRegisterRequest) => authApi.registerMentor(data), []);

  const logout = useCallback(() => {
    if (refreshToken) authApi.logout(refreshToken).catch(() => void 0);
    dispatch(logoutAction());
  }, [dispatch, refreshToken]);

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
        registerStudent,
        registerMentor,
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
