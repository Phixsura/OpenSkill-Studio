"use client";

interface Ticket { id: string; title: string; priority: string; status: string; replies: number; }
interface SupportTicketListProps { tickets: Ticket[]; openCount: number;
  onSelect: (id: string) => void; onCreate: () => void; }

const PRI_BADGE: Record<string, string> = {
  high: "bg-red-100 text-red-700", medium: "bg-yellow-100 text-yellow-700", low: "bg-gray-100 text-gray-600",
};

export function SupportTicketList({ tickets, openCount, onSelect, onCreate }: SupportTicketListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold">🎫 Support Tickets</h3>
          <p className="text-xs text-gray-400">{openCount} open</p>
        </div>
        <button onClick={onCreate} className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">New Ticket</button>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tickets.map(t => (
          <button key={t.id} onClick={() => onSelect(t.id)}
            className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-gray-400">{t.id}</span>
                <span className="text-sm font-medium">{t.title}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${PRI_BADGE[t.priority] || ""}`}>{t.priority}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                {t.replies > 0 && <span>💬 {t.replies}</span>}
                <span className={t.status === "open" ? "text-green-600" : "text-gray-400"}>{t.status}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
