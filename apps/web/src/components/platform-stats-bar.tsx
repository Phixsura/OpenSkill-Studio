"use client";

interface Stat { label: string; display: string; icon: string; }
interface PlatformStatsBarProps { stats: Stat[]; }

export function PlatformStatsBar({ stats }: PlatformStatsBarProps) {
  return (
    <div className="flex items-center justify-around rounded-xl border bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 dark:from-blue-900/10 dark:to-purple-900/10 dark:border-gray-700">
      {stats.map((s, i) => (
        <div key={i} className="text-center">
          <span className="text-xl">{s.icon}</span>
          <p className="text-2xl font-bold mt-1">{s.display}</p>
          <p className="text-xs text-gray-400">{s.label}</p>
        </div>
      ))}
    </div>
  );
}
