"use client";
interface Split { version: string; pct: number; }
interface TrafficSplitPanelProps { splits: Split[]; valid: boolean; }
export function TrafficSplitPanel({ splits, valid }: TrafficSplitPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Traffic Split</h3>
        <span className={`text-xs ${valid ? "text-green-600" : "text-red-500"}`}>
          {valid ? "✅ Valid (100%)" : "❌ Invalid"}
        </span>
      </div>
      <div className="p-4">
        <div className="flex h-4 rounded-full overflow-hidden mb-2">
          {splits.map((s, i) => (
            <div key={s.version} className={`${i === 0 ? "bg-blue-500" : i === 1 ? "bg-green-500" : "bg-yellow-500"}`}
              style={{ width: `${s.pct}%` }} title={`${s.version}: ${s.pct}%`} />
          ))}
        </div>
        <div className="flex gap-3 text-xs">
          {splits.map(s => (
            <span key={s.version} className="text-gray-400">{s.version}: {s.pct}%</span>
          ))}
        </div>
      </div>
    </div>
  );
}
