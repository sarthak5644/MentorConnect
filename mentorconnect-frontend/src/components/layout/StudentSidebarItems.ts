import { LayoutDashboard, Search, ClipboardList, CalendarCheck, MessageSquare, Bell, Star, User } from 'lucide-react';
import { SidebarItem } from './Sidebar';

export const studentSidebarItems: SidebarItem[] = [
  { label: 'Dashboard', to: '/student/dashboard', icon: LayoutDashboard },
  { label: 'Find Mentors', to: '/student/search', icon: Search },
  { label: 'My Requests', to: '/student/requests', icon: ClipboardList },
  { label: 'Bookings', to: '/student/bookings', icon: CalendarCheck },
  { label: 'Chat', to: '/student/chat', icon: MessageSquare },
  { label: 'Notifications', to: '/student/notifications', icon: Bell },
  { label: 'My Ratings', to: '/student/ratings', icon: Star },
  { label: 'Profile', to: '/student/profile', icon: User },
];