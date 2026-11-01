"use client";

interface UptimeCalculatorProps { uptimePct: number; nines: number;
  downtimeMonthSec: number; downtimeYearSec: number; display: string;
  targetPct: number; met: boolean; }

export function UptimeCalculator({ uptimePct, nines, downtimeMonthSec, downtimeYearSec, display, targetPct, met }: UptimeCalculatorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className="text-3xl font-bold text-blue-600">{uptimePct}%</div>
        <div className="text-xs text-gray-400">{nines} nines</div>
        <div className={`text-xs mt-1 ${met ? "text-green-600" : "text-red-500"}`}>
          {met ? "✅" : "❌"} SLA target: {targetPct}%
        </div>
      </div>
      <div className="grid grid-cols-2 gap-px bg-gray-200 dark:bg-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-sm font-bold">{downtimeMonthSec}s</div>
          <div className="text-[9px] text-gray-400">Downtime/Month</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-sm font-bold">{downtimeYearSec}s</div>
          <div className="text-[9px] text-gray-400">Downtime/Year</div>
        </div>
      </div>
    </div>
  );
}
