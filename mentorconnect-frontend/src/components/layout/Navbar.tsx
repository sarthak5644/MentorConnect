import { Link, useNavigate } from 'react-router-dom';
import { Sun, Moon, Bell, LogOut, Menu } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';
import { useAppDispatch } from '@/store/hooks';
import { toggleSidebar } from '@/store/uiSlice';
import { useQuery } from '@tanstack/react-query';
import { notificationsApi } from '@/api/endpoints';
import { initials } from '@/lib/utils';

export default function Navbar({ showMenuToggle }: { showMenuToggle?: boolean }) {
  const { theme, toggleTheme } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const { data: unread } = useQuery({
    queryKey: ['unread-count'],
    queryFn: notificationsApi.unreadCount,
    enabled: isAuthenticated,
    refetchInterval: 30_000,
  });

  return (
    <header className="sticky top-0 z-40 border-b border-ink-100 dark:border-ink-700 bg-paper/90 dark:bg-paper-dark/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-3">
          {showMenuToggle && (
            <button onClick={() => dispatch(toggleSidebar())} className="text-ink-500 lg:hidden">
              <Menu className="h-5 w-5" />
            </button>
          )}
          <Link to="/" className="font-display text-xl font-semibold text-ink-800 dark:text-ink-50">
            Mentor<span className="text-accent">Connect</span>
          </Link>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={toggleTheme}
            className="rounded-lg p-2 text-ink-500 hover:bg-ink-100 dark:hover:bg-ink-700"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>

          {isAuthenticated ? (
            <>
              <Link
                to={
                  user?.role.name === 'student'
                    ? '/student/notifications'
                    : user?.role.name === 'mentor'
                    ? '/mentor/notifications'
                    : '/admin/notifications'
                }
                className="relative rounded-lg p-2 text-ink-500 hover:bg-ink-100 dark:hover:bg-ink-700"
              >
                <Bell className="h-5 w-5" />
                {!!unread?.count && (
                  <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-accent text-[10px] text-white">
                    {unread.count > 9 ? '9+' : unread.count}
                  </span>
                )}
              </Link>
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/10 text-xs font-medium text-accent">
                {user ? initials(user.full_name) : ''}
              </div>
              <button
                onClick={() => {
                  logout();
                  navigate('/login');
                }}
                className="rounded-lg p-2 text-ink-500 hover:bg-ink-100 dark:hover:bg-ink-700"
                aria-label="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary">Login</Link>
              <Link to="/register" className="btn-primary">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}