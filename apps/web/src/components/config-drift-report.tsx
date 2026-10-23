"use client";

interface Diff { path: string; type: string; expected: unknown; actual: unknown; }
interface ConfigDriftReportProps { totalDrifts: number; severity: string;
  byType: Record<string, number>; diffs: Diff[]; }

const TYPE_BADGE: Record<string, string> = {
  changed: "bg-yellow-100 text-yellow-700", missing: "bg-red-100 text-red-700",
  extra: "bg-blue-100 text-blue-700",
};

export function ConfigDriftReport({ totalDrifts, severity, byType, diffs }: ConfigDriftReportProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔍 Config Drift</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          severity === "clean" ? "bg-green-100 text-green-700" :
          severity === "critical" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"
        }`}>{severity === "clean" ? "✅ No drift" : `⚠️ ${totalDrifts} drifts`}</span>
      </div>
      {totalDrifts > 0 && (
        <>
          <div className="flex gap-3 mb-3 text-xs text-gray-400">
            {Object.entries(byType).filter(([,v]) => v > 0).map(([k, v]) => (
              <span key={k}>{k}: {v}</span>
            ))}
          </div>
          <div className="space-y-2">
            {diffs.map((d, i) => (
              <div key={i} className="bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 text-sm">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs px-1.5 py-0.5 rounded ${TYPE_BADGE[d.type] || ""}`}>{d.type}</span>
                  <span className="font-mono text-xs">{d.path}</span>
                </div>
                <div className="flex gap-4 text-xs">
                  {d.expected !== null && <span className="text-red-500">- {String(d.expected)}</span>}
                  {d.actual !== null && <span className="text-green-500">+ {String(d.actual)}</span>}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
