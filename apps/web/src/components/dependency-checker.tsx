"use client";

interface DepPackage { name: string; current: string; latest: string; outdated: boolean;
  updateType: string | null; breaking: boolean; }
interface DependencyCheckerProps { packages: DepPackage[]; outdated: number; majorUpdates: number; health: string; }

const healthConfig: Record<string, { icon: string; color: string }> = {
  good: { icon: "✅", color: "text-green-600" },
  warning: { icon: "⚠️", color: "text-yellow-600" },
  critical: { icon: "🚨", color: "text-red-600" },
};

export function DependencyChecker({ packages, outdated, majorUpdates, health }: DependencyCheckerProps) {
  const cfg = healthConfig[health] ?? healthConfig.good;
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Dependencies</h3>
        <div className="flex items-center gap-2">
          <span>{cfg.icon}</span>
          <span className={`text-xs font-medium ${cfg.color}`}>{outdated} outdated{majorUpdates > 0 ? ` (${majorUpdates} major)` : ""}</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-64 overflow-y-auto">
        {packages.map(p => (
          <div key={p.name} className="flex items-center justify-between px-4 py-2">
            <span className="text-sm font-mono">{p.name}</span>
            <div className="flex items-center gap-2 text-xs">
              <span className="text-gray-400">{p.current}</span>
              {p.outdated && (
                <>
                  <span>→</span>
                  <span className={p.breaking ? "text-red-600 font-medium" : "text-green-600"}>{p.latest}</span>
                  {p.breaking && <span className="text-red-500 text-xs">breaking</span>}
                </>
              )}
              {!p.outdated && <span className="text-green-600">✓</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
