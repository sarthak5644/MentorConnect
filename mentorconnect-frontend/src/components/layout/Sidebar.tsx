import { NavLink } from 'react-router-dom';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppSelector } from '@/store/hooks';

export interface SidebarItem {
  label: string;
  to: string;
  icon: LucideIcon;
}

export default function Sidebar({ items }: { items: SidebarItem[] }) {
  const sidebarOpen = useAppSelector((s) => s.ui.sidebarOpen);

  return (
    <aside
      className={cn(
        'shrink-0 border-r border-ink-100 dark:border-ink-700 bg-white dark:bg-ink-800 transition-all',
        sidebarOpen ? 'w-60' : 'w-0 lg:w-60 overflow-hidden'
      )}
    >
      <nav className="flex flex-col gap-1 p-3">
        {items.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-accent/10 text-accent'
                  : 'text-ink-600 dark:text-ink-300 hover:bg-ink-50 dark:hover:bg-ink-700'
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}