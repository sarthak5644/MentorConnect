import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { MessageSquare } from 'lucide-react';
import { chatApi } from '@/api/endpoints';
import { PageSpinner, EmptyState } from '@/components/ui';
import ChatWindow from '@/components/chat/ChatWindow';
import ChatList from '@/components/chat/ChatList';

export default function MentorChat() {
  const { chatId } = useParams<{ chatId: string }>();
  const navigate = useNavigate();
  const { data: chats, isLoading } = useQuery({ queryKey: ['my-chats'], queryFn: chatApi.listMyChats });

  if (isLoading) return <PageSpinner />;
  if (!chats?.length) return <EmptyState icon={MessageSquare} title="No conversations yet" description="Chats start once you accept a student's request." />;

  const activeChatId = chatId ? Number(chatId) : chats[0].id;

  return (
    <div className="grid h-[calc(100vh-8rem)] grid-cols-1 gap-4 sm:grid-cols-3">
      <div className="sm:col-span-1 overflow-y-auto">
        <ChatList chats={chats} activeChatId={activeChatId} onSelect={(id) => navigate(`/mentor/chat/${id}`)} />
      </div>
      <div className="sm:col-span-2">
        <ChatWindow chatId={activeChatId} />
      </div>
    </div>
  );
}