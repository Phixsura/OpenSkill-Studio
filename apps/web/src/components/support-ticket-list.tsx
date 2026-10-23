"use client";

interface Ticket { id: string; subject: string; priority: string; status: string; createdAt: string; }
interface SupportTicketListProps { tickets: Ticket[]; openCount: number; hasUrgent: boolean; }

const priorityBadge: Record<string, string> = {
  low: "bg-gray-100 text-gray-600", medium: "bg-blue-100 text-blue-700",
  high: "bg-orange-100 text-orange-700", urgent: "bg-red-100 text-red-700",
};
const statusBadge: Record<string, string> = {
  open: "bg-green-100 text-green-700", in_progress: "bg-blue-100 text-blue-700",
  waiting: "bg-yellow-100 text-yellow-700", resolved: "bg-gray-100 text-gray-500",
};

export function SupportTicketList({ tickets, openCount, hasUrgent }: SupportTicketListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Support Tickets</h3>
        <div className="flex items-center gap-2">
          {hasUrgent && <span className="animate-pulse text-xs text-red-600">🚨 Urgent</span>}
          <span className="text-xs text-gray-400">{openCount} open</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {tickets.map(t => (
          <div key={t.id} className="flex items-center justify-between px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <code className="text-xs text-gray-400">{t.id}</code>
                <span className="text-sm font-medium">{t.subject}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs ${priorityBadge[t.priority] ?? ""} dark:bg-opacity-30`}>{t.priority}</span>
              <span className={`rounded px-1.5 py-0.5 text-xs ${statusBadge[t.status] ?? ""} dark:bg-opacity-30`}>{t.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
