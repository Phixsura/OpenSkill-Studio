"use client";

interface Ticket { ticket_id: string; subject: string; priority: string; status: string; created_at: string; }
interface SupportTicketListProps { tickets: Ticket[]; onSelect: (id: string) => void; }

const priorityColors: Record<string, string> = {
  low: "bg-gray-100 text-gray-600 dark:bg-gray-800", medium: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/30", critical: "bg-red-100 text-red-700 dark:bg-red-900/30",
};
const statusColors: Record<string, string> = {
  open: "text-green-600", in_progress: "text-blue-600", waiting: "text-yellow-600",
  resolved: "text-gray-400", closed: "text-gray-300",
};

export function SupportTicketList({ tickets, onSelect }: SupportTicketListProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Support Tickets</h2>
      {tickets.length === 0 ? (
        <p className="text-sm text-gray-400">No tickets</p>
      ) : (
        <div className="space-y-2">
          {tickets.map(t => (
            <button key={t.ticket_id} onClick={() => onSelect(t.ticket_id)}
              className="flex w-full items-center justify-between rounded-lg border p-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
              <div>
                <p className="text-sm font-medium">{t.subject}</p>
                <p className="text-xs text-gray-400">{t.ticket_id} · {new Date(t.created_at).toLocaleDateString()}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`rounded-full px-2 py-0.5 text-xs ${priorityColors[t.priority] ?? ""}`}>{t.priority}</span>
                <span className={`text-xs font-medium ${statusColors[t.status] ?? ""}`}>{t.status}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
