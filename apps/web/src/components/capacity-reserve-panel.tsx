"use client";

interface CapacityReservePanelProps { totalReserved: number; totalUtilized: number;
  utilizationPct: number; underutilized: string[]; wasteCount: number; }

export function CapacityReservePanel({ totalReserved, totalUtilized, utilizationPct, underutilized, wasteCount }: CapacityReservePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Capacity Reservations</h3>
        <span className="text-xs text-gray-400">{utilizationPct}% utilized{wasteCount > 0 ? ` · ⚠ ${wasteCount} wasted` : ""}</span>
      </div>
      <div className="grid grid-cols-2 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{totalReserved}</div>
          <div className="text-[10px] text-gray-400">Reserved</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{totalUtilized}</div>
          <div className="text-[10px] text-gray-400">Utilized</div>
        </div>
      </div>
      {underutilized.length > 0 && (
        <div className="p-3 text-xs text-yellow-600">
          ⚠ Underutilized: {underutilized.join(", ")}
        </div>
      )}
    </div>
  );
}
