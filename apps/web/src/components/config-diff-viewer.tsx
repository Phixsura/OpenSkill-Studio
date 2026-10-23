"use client";

interface Diff { key: string; type: string; [env: string]: unknown; }
interface ConfigDiffViewerProps { envA: string; envB: string; diffs: Diff[];
  sameCount: number; driftPct: number; }

const typeLabel: Record<string, { icon: string; color: string }> = {
  changed: { icon: "~", color: "text-yellow-600" },
  added: { icon: "+", color: "text-green-600" },
  removed: { icon: "-", color: "text-red-600" },
};

export function ConfigDiffViewer({ envA, envB, diffs, sameCount, driftPct }: ConfigDiffViewerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{envA} vs {envB}</h2>
        <span className={`text-sm font-medium ${driftPct > 20 ? "text-red-600" : driftPct > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {driftPct}% drift
        </span>
      </div>
      <p className="text-xs text-gray-400">{sameCount} identical · {diffs.length} different</p>
      <div className="space-y-1">
        {diffs.map(d => {
          const t = typeLabel[d.type] ?? typeLabel.changed;
          return (
            <div key={d.key} className="flex items-center gap-2 rounded border px-3 py-1.5 font-mono text-xs dark:border-gray-700">
              <span className={`w-4 font-bold ${t.color}`}>{t.icon}</span>
              <span className="w-32 font-bold">{d.key}</span>
              {d.type === "changed" && (
                <>
                  <span className="text-red-400 line-through">{String(d[envA] ?? "")}</span>
                  <span className="text-gray-400">→</span>
                  <span className="text-green-400">{String(d[envB] ?? "")}</span>
                </>
              )}
              {d.type === "added" && <span className="text-green-400">{String(d[envB] ?? "")}</span>}
              {d.type === "removed" && <span className="text-red-400 line-through">{String(d[envA] ?? "")}</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
