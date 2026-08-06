import { BarChart3, UserCheck, Users, Briefcase, FolderTree, Flag, MessageCircleWarning, Bell, ScrollText } from 'lucide-react';
import { SidebarItem } from './Sidebar';

export const adminSidebarItems: SidebarItem[] = [
  { label: 'Analytics', to: '/admin/analytics', icon: BarChart3 },
  { label: 'Mentor Approval', to: '/admin/mentor-approval', icon: UserCheck },
  { label: 'Students', to: '/admin/students', icon: Users },
  { label: 'Mentors', to: '/admin/mentors', icon: Briefcase },
  { label: 'Categories', to: '/admin/categories', icon: FolderTree },
  { label: 'Reports', to: '/admin/reports', icon: Flag },
  { label: 'Complaints', to: '/admin/complaints', icon: MessageCircleWarning },
  { label: 'Notifications', to: '/admin/notifications', icon: Bell },
  { label: 'Audit Logs', to: '/admin/audit-logs', icon: ScrollText },
];