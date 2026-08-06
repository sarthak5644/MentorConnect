import { useEffect, useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Send, Paperclip } from 'lucide-react';
import { chatApi } from '@/api/endpoints';
import { useAuth } from '@/context/AuthContext';
import { Spinner, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { cn, formatTime } from '@/lib/utils';

export default function ChatWindow({ chatId }: { chatId: number }) {
  const { user } = useAuth();
  const { showToast } = useToast();
  const qc = useQueryClient();
  const [text, setText] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const { data: messages, isLoading } = useQuery({
    queryKey: ['messages', chatId],
    queryFn: () => chatApi.listMessages(chatId),
    refetchInterval: 5000,
  });

  useEffect(() => {
    chatApi.markRead(chatId).catch(() => void 0);
  }, [chatId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMutation = useMutation({
    mutationFn: () => chatApi.sendMessage(chatId, { content: text }),
    onSuccess: () => {
      setText('');
      qc.invalidateQueries({ queryKey: ['messages', chatId] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const attachMutation = useMutation({
    mutationFn: (file: File) => {
      const fd = new FormData();
      fd.append('file', file);
      return chatApi.sendAttachment(chatId, fd);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages', chatId] }),
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center rounded-xl border border-ink-100 dark:border-ink-700">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col rounded-xl border border-ink-100 dark:border-ink-700 bg-white dark:bg-ink-800">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages?.map((m) => {
          const isMine = m.sender_id === user?.id;
          return (
            <div key={m.id} className={cn('flex', isMine ? 'justify-end' : 'justify-start')}>
              <div
                className={cn(
                  'max-w-[75%] rounded-2xl px-3.5 py-2 text-sm',
                  isMine ? 'bg-accent text-white rounded-br-sm' : 'bg-ink-100 dark:bg-ink-700 text-ink-800 dark:text-ink-100 rounded-bl-sm'
                )}
              >
                {m.attachment_path ? (
                  <a href={m.attachment_path} target="_blank" rel="noreferrer" className="underline">
                    Attachment
                  </a>
                ) : (
                  m.content
                )}
                <p className={cn('mt-1 text-[10px]', isMine ? 'text-white/70' : 'text-ink-400')}>{formatTime(m.created_at)}</p>
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (text.trim()) sendMutation.mutate();
        }}
        className="flex items-center gap-2 border-t border-ink-100 dark:border-ink-700 p-3"
      >
        <input
          ref={fileRef}
          type="file"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && attachMutation.mutate(e.target.files[0])}
        />
        <button type="button" onClick={() => fileRef.current?.click()} className="text-ink-400 hover:text-accent">
          <Paperclip className="h-5 w-5" />
        </button>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type a message..."
          className="input-field flex-1"
        />
        <button type="submit" className="btn-primary px-3">
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}