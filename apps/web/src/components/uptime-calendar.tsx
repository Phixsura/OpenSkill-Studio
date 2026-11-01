"use client";

interface DayStatus { date: string; uptime_pct: number; status: string; }
interface UptimeCalendarProps { days: DayStatus[]; uptimePct: number; period: string; }

const STATUS_COLORS: Record<string, string> = { good: "bg-green-500", degraded: "bg-yellow-500", outage: "bg-red-500" };

export function UptimeCalendar({ days, uptimePct, period }: UptimeCalendarProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Uptime</h3>
        <div className="text-right">
          <span className={`text-xl font-bold ${uptimePct >= 99.9 ? "text-green-600" : "text-yellow-600"}`}>{uptimePct}%</span>
          <p className="text-xs text-gray-400">{period}</p>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-0.5">
        {days.map(d => (
          <div key={d.date} className={`h-3 w-3 rounded-sm ${STATUS_COLORS[d.status] || "bg-gray-200"}`}
            title={`${d.date}: ${d.uptime_pct}%`} />
        ))}
      </div>
      <div className="mt-2 flex justify-between text-xs text-gray-400">
        <span>{days.length} days</span>
        <div className="flex gap-2">
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-sm bg-green-500" /> Good</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-sm bg-yellow-500" /> Degraded</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-sm bg-red-500" /> Outage</span>
        </div>
      </div>
    </div>
  );
}
