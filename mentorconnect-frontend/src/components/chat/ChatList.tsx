import { Chat } from '@/types';
import { cn } from '@/lib/utils';
import { formatDateTime } from '@/lib/utils';

export default function ChatList({
  chats, activeChatId, onSelect,
}: { chats: Chat[]; activeChatId: number; onSelect: (id: number) => void }) {
  return (
    <div className="space-y-1">
      {chats.map((c) => (
        <button
          key={c.id}
          onClick={() => onSelect(c.id)}
          className={cn(
            'w-full rounded-lg border px-3 py-2.5 text-left text-sm transition-colors',
            c.id === activeChatId
              ? 'border-accent bg-accent/10'
              : 'border-ink-100 dark:border-ink-700 hover:border-accent'
          )}
        >
          <p className="font-medium text-ink-800 dark:text-ink-50">Conversation #{c.id}</p>
          <p className="text-xs text-ink-400">
            {c.last_message_at ? formatDateTime(c.last_message_at) : 'No messages yet'}
          </p>
        </button>
      ))}
    </div>
  );
}