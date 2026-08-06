import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar, { SidebarItem } from './Sidebar';

export default function DashboardLayout({ items }: { items: SidebarItem[] }) {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar showMenuToggle />
      <div className="flex flex-1">
        <Sidebar items={items} />
        <main className="flex-1 min-w-0 p-4 sm:p-6 bg-paper dark:bg-paper-dark">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}