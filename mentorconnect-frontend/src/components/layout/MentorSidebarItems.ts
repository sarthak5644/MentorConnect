import { LayoutDashboard, User, GraduationCap, Trophy, FileText, CalendarClock, ClipboardList, MessageSquare, Bell, Star } from 'lucide-react';
import { SidebarItem } from './Sidebar';

export const mentorSidebarItems: SidebarItem[] = [
  { label: 'Dashboard', to: '/mentor/dashboard', icon: LayoutDashboard },
  { label: 'Profile', to: '/mentor/profile', icon: User },
  { label: 'Qualifications', to: '/mentor/qualifications', icon: GraduationCap },
  { label: 'Achievements', to: '/mentor/achievements', icon: Trophy },
  { label: 'Documents', to: '/mentor/documents', icon: FileText },
  { label: 'Availability', to: '/mentor/availability', icon: CalendarClock },
  { label: 'Requests', to: '/mentor/requests', icon: ClipboardList },
  { label: 'Chat', to: '/mentor/chat', icon: MessageSquare },
  { label: 'Notifications', to: '/mentor/notifications', icon: Bell },
  { label: 'Reviews', to: '/mentor/reviews', icon: Star },
];