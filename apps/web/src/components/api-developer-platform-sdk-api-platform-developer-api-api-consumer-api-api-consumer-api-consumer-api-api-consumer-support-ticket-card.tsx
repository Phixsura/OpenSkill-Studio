"use client";

interface Ticket { id: string; subject: string; priority: string; status: string; createdAt: string; replyCount: number; }
interface Props { tickets: Ticket[]; consumerId: string; appName: string; }

const priorityColors: Record<string, string> = {
  urgent: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  high: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  normal: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  low: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
};
const statusIcons: Record<string, string> = { open: "🟢", in_progress: "🟡", waiting: "⏳", resolved: "✅", closed: "⚫" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerSupportTicketCard({ tickets, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎫 Support Tickets</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {tickets.filter(t => t.status === "open").length} open</p>
      </div>
      {tickets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tickets</p>
      ) : (
        <div className="space-y-2">
          {tickets.slice(0, 6).map((t) => (
            <div key={t.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{t.subject}</span>
                <span className={`rounded px-1 py-0.5 text-[9px] font-medium ${priorityColors[t.priority] ?? ""}`}>{t.priority}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">{statusIcons[t.status] ?? ""} {t.status} · {t.replyCount} replies · {t.createdAt}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
