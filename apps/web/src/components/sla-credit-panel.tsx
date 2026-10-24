"use client";
interface SlaCreditPanelProps { slaMet: boolean; creditPct: number; creditAmount: number;
  uptimePct: number; gap: number; monthlyRevenue: number; }
export function SlaCreditPanel({ slaMet, creditPct, creditAmount, uptimePct, gap, monthlyRevenue }: SlaCreditPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${slaMet ? "bg-green-500" : "bg-red-500"}`}>
        {slaMet ? "✅ SLA Met — No Credits Owed" : `⚠ SLA Breach — ${creditPct}% Credit (${gap}% gap)`}
      </div>
      {!slaMet && (
        <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
          <div><span className="text-gray-400">Uptime</span><div className="font-bold text-lg">{uptimePct}%</div></div>
          <div><span className="text-gray-400">Credit</span><div className="font-bold text-red-500 text-lg">${creditAmount.toLocaleString()}</div></div>
          <div><span className="text-gray-400">Revenue</span><div className="font-bold text-lg">${monthlyRevenue.toLocaleString()}</div></div>
        </div>
      )}
    </div>
  );
}
