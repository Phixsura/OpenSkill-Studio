"use client";
interface StorageUsagePanelProps { totalGb: number; limitGb: number; pctUsed: number;
  byType: Record<string, number>; monthsUntilFull: number; }
export function StorageUsagePanel({ totalGb, limitGb, pctUsed, byType, monthsUntilFull }: StorageUsagePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💾 Storage Usage</h3>
        <span className={`text-xs font-bold ${pctUsed > 80 ? "text-red-500" : "text-green-600"}`}>
          {totalGb}GB / {limitGb}GB ({pctUsed}%) · {monthsUntilFull}mo left
        </span>
      </div>
      <div className="p-4">
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full mb-3">
          <div className={`h-full rounded-full ${pctUsed > 90 ? "bg-red-500" : pctUsed > 70 ? "bg-yellow-500" : "bg-blue-500"}`}
            style={{ width: `${Math.min(pctUsed, 100)}%` }} />
        </div>
        <div className="flex gap-3 text-xs">
          {Object.entries(byType).map(([t, gb]) => (
            <span key={t} className="text-gray-400">{t}: {gb}GB</span>
          ))}
        </div>
      </div>
    </div>
  );
}
