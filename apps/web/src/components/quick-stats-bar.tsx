"use client";

interface QuickStat { label: string; display: string; icon: string; }
interface QuickStatsBarProps { stats: QuickStat[]; }

export function QuickStatsBar({ stats }: QuickStatsBarProps) {
  return (
    <div className="flex gap-4 overflow-x-auto py-2">
      {stats.map(s => (
        <div key={s.label} className="flex items-center gap-1.5 text-sm whitespace-nowrap">
          <span>{s.icon}</span>
          <span className="font-bold">{s.display}</span>
          <span className="text-xs text-gray-400">{s.label}</span>
        </div>
      ))}
    </div>
  );
}
