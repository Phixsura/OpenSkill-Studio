"use client";

interface TicketInfo {
  ticket_id: string;
  subject: string;
  priority: "low" | "medium" | "high" | "urgent";
  status: "open" | "in_progress" | "waiting" | "resolved" | "closed";
  assignee: string;
}

interface APISupportTicketCardProps {
  tickets: TicketInfo[];
  appName: string;
}

const prioStyle: Record<string, string> = {
  low: "bg-gray-100 text-gray-500 dark:bg-gray-800",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  urgent: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function APISupportTicketCard({ tickets, appName }: APISupportTicketCardProps) {
  const open = tickets.filter((t) => !["resolved", "closed"].includes(t.status)).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎫 Support Tickets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{open} open / {tickets.length} total</span>
      </div>

      {tickets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No support tickets</p>
      ) : (
        <div className="space-y-1.5">
          {tickets.map((t) => (
            <div key={t.ticket_id} className={`flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800 ${["resolved", "closed"].includes(t.status) ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${prioStyle[t.priority]}`}>{t.priority}</span>
                <span className="text-xs text-gray-700 dark:text-gray-300">{t.subject}</span>
              </div>
              <span className="text-[10px] text-gray-400">{t.status.replace("_", " ")}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
