"use client";

interface InboxMessage { message_id: string; type: string; type_label: string; icon: string;
  title: string; body: string; read: boolean; created_at: string; }
interface DeveloperInboxViewProps { messages: InboxMessage[]; unreadCount: number;
  onRead: (id: string) => void; onReadAll: () => void; }

export function DeveloperInboxView({ messages, unreadCount, onRead, onReadAll }: DeveloperInboxViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold">Inbox</h2>
          {unreadCount > 0 && (
            <span className="flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-red-500 px-1.5 text-xs text-white">
              {unreadCount}
            </span>
          )}
        </div>
        {unreadCount > 0 && (
          <button onClick={onReadAll} className="text-xs text-blue-500">Mark all read</button>
        )}
      </div>
      <div className="space-y-1.5">
        {messages.map(m => (
          <button key={m.message_id} onClick={() => onRead(m.message_id)}
            className={`flex w-full items-start gap-3 rounded-lg border p-3 text-left ${!m.read ? "bg-blue-50/30 dark:bg-blue-900/5" : ""} dark:border-gray-700`}>
            <span className="text-lg">{m.icon}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <p className={`text-sm ${!m.read ? "font-semibold" : ""}`}>{m.title}</p>
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] dark:bg-gray-800">{m.type_label}</span>
              </div>
              <p className="mt-0.5 text-xs text-gray-400">{m.body}</p>
              <p className="mt-0.5 text-[10px] text-gray-300">{new Date(m.created_at).toLocaleString()}</p>
            </div>
            {!m.read && <span className="mt-1 h-2 w-2 flex-shrink-0 rounded-full bg-blue-500" />}
          </button>
        ))}
        {messages.length === 0 && <p className="py-4 text-center text-sm text-gray-400">No messages</p>}
      </div>
    </div>
  );
}
