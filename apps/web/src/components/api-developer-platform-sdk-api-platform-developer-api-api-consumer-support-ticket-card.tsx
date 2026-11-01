"use client";

interface TicketInfo { ticket_id: string; consumer_id: string; subject: string; priority: string; status: string; }
interface Props { tickets: TicketInfo[]; openCount: number; urgentCount: number; appName: string; }

const prioColor: Record<string, string> = { low: "text-gray-400", medium: "text-blue-600 dark:text-blue-400", high: "text-orange-600 dark:text-orange-400", urgent: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSupportTicketCard({ tickets, openCount, urgentCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎫 Support Tickets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {openCount} open</p>
        </div>
        {urgentCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔥 {urgentCount} urgent</span>}
      </div>
      {tickets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tickets</p>
      ) : (
        <div className="space-y-1">
          {tickets.map((t) => (
            <div key={t.ticket_id} className="flex items-center justify-between text-[11px]">
              <span className="truncate text-gray-700 dark:text-gray-300">{t.subject}</span>
              <span className={prioColor[t.priority] ?? "text-gray-400"}>{t.priority}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
