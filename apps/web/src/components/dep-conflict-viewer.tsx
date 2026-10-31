"use client";

interface Requirement { package: string; constraint: string; requiredBy: string; }
interface Conflict { package: string; requirements: Requirement[]; reason: string; }
interface Resolution { package: string; version: string; strategy: string; }

const strategyBadge: Record<string, { bg: string; label: string }> = {
  newest: { bg: "bg-green-100 text-green-700", label: "Newest Compatible" },
  oldest: { bg: "bg-blue-100 text-blue-700", label: "Oldest Compatible" },
  force: { bg: "bg-red-100 text-red-700", label: "⚠️ Forced" },
};

export function DepConflictViewer({ conflicts, resolutions }: {
  conflicts: Conflict[]; resolutions: Resolution[];
}) {
  return (
    <div className="space-y-4">
      {conflicts.length > 0 && (
        <div>
          <h3 className="font-bold text-sm text-red-600 mb-2">⚠️ Conflicts ({conflicts.length})</h3>
          {conflicts.map((c, i) => (
            <div key={i} className="border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10 rounded-xl p-3 mb-2">
              <span className="font-mono font-bold text-sm">{c.package}</span>
              <div className="mt-1 space-y-0.5">
                {c.requirements.map((r, j) => (
                  <div key={j} className="text-xs flex items-center gap-2">
                    <span className="text-gray-500">{r.requiredBy}</span>
                    <span>→</span>
                    <code className="bg-red-100 dark:bg-red-900/20 px-1 rounded">{r.constraint}</code>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {resolutions.length > 0 && (
        <div>
          <h3 className="font-bold text-sm mb-2">📦 Resolutions ({resolutions.length})</h3>
          <div className="space-y-1">
            {resolutions.map(r => {
              const badge = strategyBadge[r.strategy] || strategyBadge.newest;
              return (
                <div key={r.package} className="flex items-center justify-between border dark:border-gray-700 rounded-lg p-2 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-medium">{r.package}</span>
                    <code className="text-xs bg-blue-50 dark:bg-blue-900/10 px-1.5 py-0.5 rounded">v{r.version}</code>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${badge.bg}`}>{badge.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {conflicts.length === 0 && resolutions.length === 0 && (
        <div className="text-center text-green-600 py-6">
          <span className="text-2xl block">✅</span>
          <span className="text-sm font-medium mt-1 block">No dependency conflicts</span>
        </div>
      )}
    </div>
  );
}
