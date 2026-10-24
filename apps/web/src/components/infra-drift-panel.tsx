"use client";

interface Drift { key: string; desired: unknown; actual: unknown; type: string; }
interface InfraDriftPanelProps { drifts: Drift[]; hasDrift: boolean;
  driftedCount: number; totalResources: number; driftPct: number; }

const TYPE_COLORS: Record<string, string> = {
  changed: "text-yellow-600", missing: "text-red-500", extra: "text-blue-500",
};

export function InfraDriftPanel({ drifts, hasDrift, driftedCount, totalResources, driftPct }: InfraDriftPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Infrastructure Drift</h3>
        <span className={`text-xs ${hasDrift ? "text-yellow-600" : "text-green-600"}`}>
          {hasDrift ? `⚠ ${driftedCount}/${totalResources} drifted (${driftPct}%)` : "✅ No Drift"}
        </span>
      </div>
      {drifts.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {drifts.map(d => (
            <div key={d.key} className="flex justify-between px-4 py-1.5 text-xs">
              <span className={`font-mono ${TYPE_COLORS[d.type] ?? ""}`}>{d.type}: {d.key}</span>
              <span className="text-gray-400">{String(d.desired ?? "—")} → {String(d.actual ?? "—")}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
