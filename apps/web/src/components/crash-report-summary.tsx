"use client";

interface CrashGroup { signature: string; message: string; count: number; affected_users: number; os_list: string[]; last_seen: string; }
interface CrashReportSummaryProps { totalCrashes: number; uniqueIssues: number; crashFreeRate: number; groups: CrashGroup[]; }

export function CrashReportSummary({ totalCrashes, uniqueIssues, crashFreeRate, groups }: CrashReportSummaryProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Crash Reports</h2>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg bg-red-50 p-3 text-center dark:bg-red-900/10">
          <p className="text-2xl font-bold text-red-600">{totalCrashes}</p>
          <p className="text-xs text-gray-500">Total Crashes</p>
        </div>
        <div className="rounded-lg bg-orange-50 p-3 text-center dark:bg-orange-900/10">
          <p className="text-2xl font-bold text-orange-600">{uniqueIssues}</p>
          <p className="text-xs text-gray-500">Unique Issues</p>
        </div>
        <div className="rounded-lg bg-green-50 p-3 text-center dark:bg-green-900/10">
          <p className="text-2xl font-bold text-green-600">{crashFreeRate}%</p>
          <p className="text-xs text-gray-500">Crash-Free</p>
        </div>
      </div>
      <div className="space-y-2">
        {groups.map(g => (
          <div key={g.signature} className="flex items-center justify-between rounded border p-3 dark:border-gray-700">
            <div>
              <p className="text-sm font-medium">{g.message}</p>
              <p className="text-xs text-gray-400">{g.affected_users} users · {g.os_list.join(", ")}</p>
            </div>
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-bold text-red-700 dark:bg-red-900/30">{g.count}×</span>
          </div>
        ))}
      </div>
    </div>
  );
}
