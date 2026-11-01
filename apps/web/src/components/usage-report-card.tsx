"use client";

interface UsageReportCardProps { period: string; apiCalls: number; uniqueUsers: number; uptimePct: number; highlights: string[]; }

export function UsageReportCard({ period, apiCalls, uniqueUsers, uptimePct, highlights }: UsageReportCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Usage Report</h3>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700">{period}</span>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-4 text-center">
        <div><p className="text-xl font-bold">{apiCalls.toLocaleString()}</p><p className="text-xs text-gray-400">API Calls</p></div>
        <div><p className="text-xl font-bold">{uniqueUsers}</p><p className="text-xs text-gray-400">Users</p></div>
        <div><p className="text-xl font-bold">{uptimePct}%</p><p className="text-xs text-gray-400">Uptime</p></div>
      </div>
      {highlights.length > 0 && (
        <ul className="mt-3 space-y-1">
          {highlights.map((h, i) => <li key={i} className="text-xs text-gray-600 dark:text-gray-400">{h}</li>)}
        </ul>
      )}
    </div>
  );
}
