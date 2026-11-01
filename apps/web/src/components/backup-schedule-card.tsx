"use client";

interface BackupScheduleCardProps { name: string; frequency: string; targets: string[];
  retentionDays: number; totalBackups: number; totalSizeMb: number; onRunNow: () => void; }

const FREQ_ICONS: Record<string, string> = {
  hourly: "⏰", daily: "📅", weekly: "📆", monthly: "🗓️",
};

export function BackupScheduleCard({ name, frequency, targets, retentionDays, totalBackups, totalSizeMb, onRunNow }: BackupScheduleCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">{FREQ_ICONS[frequency] ?? "💾"} {name}</h3>
          <div className="text-xs text-gray-400 mt-0.5 capitalize">{frequency} · {retentionDays}d retention</div>
        </div>
        <button onClick={onRunNow} className="px-3 py-1 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600">Run Now</button>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{totalBackups}</div>
          <div className="text-[10px] text-gray-400">Backups</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{totalSizeMb}</div>
          <div className="text-[10px] text-gray-400">MB Total</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{targets.length}</div>
          <div className="text-[10px] text-gray-400">Targets</div>
        </div>
      </div>
      <div className="p-3 flex flex-wrap gap-1">
        {targets.map(t => (
          <span key={t} className="px-2 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 rounded capitalize">{t}</span>
        ))}
      </div>
    </div>
  );
}
