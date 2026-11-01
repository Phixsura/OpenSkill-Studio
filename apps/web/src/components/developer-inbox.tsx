"use client";

interface Message { from_type: string; subject: string; body: string; priority: string; read: boolean; created_at: string; }
interface DeveloperInboxProps { messages: Message[]; onRead: (index: number) => void; }

const TYPE_ICONS: Record<string, string> = { system: "🔔", review: "⭐", support: "💬", team: "👥", marketplace: "📦" };

export function DeveloperInbox({ messages, onRead }: DeveloperInboxProps) {
  if (messages.length === 0) return <p className="p-4 text-center text-sm text-gray-400">Inbox empty 📭</p>;
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold">Inbox ({messages.filter(m => !m.read).length} unread)</h3>
      </div>
      <ul className="max-h-64 overflow-y-auto">
        {messages.map((m, i) => (
          <li key={i} onClick={() => onRead(i)}
            className={`cursor-pointer border-b px-3 py-2 dark:border-gray-700 ${m.read ? "opacity-60" : ""} ${m.priority === "urgent" ? "border-l-2 border-l-red-500" : ""}`}>
            <div className="flex items-center gap-2 text-sm">
              <span>{TYPE_ICONS[m.from_type] || "📌"}</span>
              <span className={`flex-1 ${m.read ? "" : "font-semibold"}`}>{m.subject}</span>
              <span className="text-xs text-gray-400">{m.created_at.slice(0, 10)}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
