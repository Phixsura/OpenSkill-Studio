"use client";

interface BurnWindow { window: string; burnRate: number; severity: string; budgetConsumedPct: number; }
interface SloBurnCardProps { sloTarget: number; windows: BurnWindow[]; alerting: boolean; }

const SEV_STYLE: Record<string, string> = { ok: "text-green-600", warning: "text-yellow-600", critical: "text-red-600" };

export function SloBurnCard({ sloTarget, windows, alerting }: SloBurnCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔥 SLO Burn Rate</h3>
        <span className={`text-xs font-bold ${alerting ? "text-red-500" : "text-green-600"}`}>
          {alerting ? "⚠ ALERTING" : "✅ OK"} · SLO {(sloTarget * 100).toFixed(1)}%
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {windows.map(w => (
          <div key={w.window} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono">{w.window}</span>
            <div className="flex items-center gap-3">
              <span className="text-gray-400">{w.budgetConsumedPct}% consumed</span>
              <span className={`font-bold ${SEV_STYLE[w.severity] ?? ""}`}>{w.burnRate}x</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
