"use client";

interface DriftResult { drifted: boolean; severity: string; missing: string[];
  extra: string[]; changed: { key: string; expected: string; actual: string }[]; totalIssues: number; }
interface ConfigDriftViewerProps { baseline: string; comparisons: Record<string, DriftResult>; driftedCount: number; }

const SEV: Record<string, string> = { critical: "text-red-600", warning: "text-yellow-600", info: "text-blue-500", ok: "text-green-600" };

export function ConfigDriftViewer({ baseline, comparisons, driftedCount }: ConfigDriftViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚙️ Config Drift</h3>
        <span className="text-xs text-gray-400">vs {baseline} · {driftedCount} drifted</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(comparisons).map(([env, r]) => (
          <div key={env} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-1">
              <span className="font-semibold">{env}</span>
              <span className={SEV[r.severity] ?? ""}>{r.severity} · {r.totalIssues} issues</span>
            </div>
            {r.missing.length > 0 && <div className="text-xs text-red-500">Missing: {r.missing.join(", ")}</div>}
            {r.extra.length > 0 && <div className="text-xs text-blue-500">Extra: {r.extra.join(", ")}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
