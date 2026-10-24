"use client";

interface BuildStatusPanelProps { total: number; passed: number; failed: number;
  running: number; passRate: number; avgDurationSec: number; health: string; }

const HEALTH_STYLES: Record<string, string> = {
  green: "text-green-600", yellow: "text-yellow-600", red: "text-red-600",
};

export function BuildStatusPanel({ total, passed, failed, running, passRate, avgDurationSec, health }: BuildStatusPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏗️ Build Status</h3>
        <span className={`text-xs font-medium ${HEALTH_STYLES[health] ?? ""}`}>{passRate}% pass rate</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Total", v: total }, { l: "Passed", v: passed },
          { l: "Failed", v: failed }, { l: "Avg", v: `${avgDurationSec}s` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
