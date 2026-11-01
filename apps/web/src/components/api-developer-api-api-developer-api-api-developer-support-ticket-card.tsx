"use client";

interface TicketInfo { ticket_id: string; developer_id: string; subject: string; priority: string; status: string; }
interface Props { tickets: TicketInfo[]; openCount: number; avgResolutionHours: number; appName: string; }

const pColor: Record<string, string> = { urgent: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700", normal: "bg-blue-100 text-blue-700", low: "bg-gray-100 text-gray-600" };
const sDot: Record<string, string> = { open: "bg-yellow-500", in_progress: "bg-blue-500", waiting: "bg-gray-400", resolved: "bg-green-500", closed: "bg-gray-300" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicketCard({ tickets, openCount, avgResolutionHours, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎫 Support Tickets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          {openCount > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] text-yellow-700">{openCount} open</span>}
          <p className="text-[9px] text-gray-400 mt-0.5">avg resolution: {avgResolutionHours}h</p>
        </div>
      </div>
      {tickets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tickets</p>
      ) : (
        <div className="space-y-1.5">
          {tickets.map((t) => (
            <div key={t.ticket_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${sDot[t.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{t.subject}</span>
              </div>
              <span className={`rounded px-1 py-0.5 text-[9px] ${pColor[t.priority] ?? ""}`}>{t.priority}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
