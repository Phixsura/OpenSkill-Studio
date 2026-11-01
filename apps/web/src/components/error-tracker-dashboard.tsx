"use client";

interface ErrorGroup { fingerprint: string; message: string; count: number;
  firstSeen: string; lastSeen: string; affectedUsers: number; }
interface ErrorTrackerDashboardProps { groups: ErrorGroup[]; totalErrors: number; uniqueErrors: number; }

export function ErrorTrackerDashboard({ groups, totalErrors, uniqueErrors }: ErrorTrackerDashboardProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Error Tracker</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{totalErrors} total</span>
          <span>{uniqueErrors} unique</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {groups.map(g => (
          <div key={g.fingerprint} className="px-4 py-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-red-600 truncate max-w-[300px]">{g.message}</p>
              <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs text-white">{g.count}×</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">{g.affectedUsers} users · Last: {new Date(g.lastSeen).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
