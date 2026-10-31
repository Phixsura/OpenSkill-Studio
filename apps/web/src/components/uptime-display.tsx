"use client";

interface UptimeDisplayProps { uptimePct: number; nines: number; ninesLabel: string;
  downtimeMinutes: number; budgetMinutes: number; }

export function UptimeDisplay({ uptimePct, nines, ninesLabel, downtimeMinutes, budgetMinutes }: UptimeDisplayProps) {
  const used = budgetMinutes > 0 ? Math.round((downtimeMinutes / budgetMinutes) * 100) : 0;
  const color = uptimePct >= 99.9 ? "text-green-600" : uptimePct >= 99 ? "text-yellow-600" : "text-red-600";

  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="text-center">
        <p className={`text-4xl font-bold tabular-nums ${color}`}>{uptimePct}%</p>
        <p className="text-sm text-gray-400 mt-1">{ninesLabel} availability</p>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-center">
        <div>
          <p className="text-lg font-bold">{downtimeMinutes}m</p>
          <p className="text-xs text-gray-400">Downtime used</p>
        </div>
        <div>
          <p className="text-lg font-bold">{budgetMinutes}m</p>
          <p className="text-xs text-gray-400">Budget remaining</p>
        </div>
      </div>
      <div className="mt-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${used > 80 ? "bg-red-500" : "bg-green-500"}`} style={{ width: `${Math.min(used, 100)}%` }} />
      </div>
      <p className="mt-1 text-center text-xs text-gray-400">{used}% of downtime budget used</p>
    </div>
  );
}
