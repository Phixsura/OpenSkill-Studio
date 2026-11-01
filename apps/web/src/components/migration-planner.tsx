"use client";

interface MigrationStep { order: number; name: string; description: string; type: string;
  risk: string; reversible: boolean; estimated_seconds: number; }
interface MigrationPlannerProps { steps: MigrationStep[]; totalEstimatedSeconds: number; hasIrreversible: boolean; }

const riskColors: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-orange-600", critical: "text-red-600",
};

export function MigrationPlanner({ steps, totalEstimatedSeconds, hasIrreversible }: MigrationPlannerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Migration Plan</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{steps.length} steps</span>
          <span>~{totalEstimatedSeconds}s</span>
          {hasIrreversible && <span className="text-red-500">⚠ Has irreversible steps</span>}
        </div>
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.order} className="flex items-start gap-3 rounded-lg border p-3 dark:border-gray-700">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-bold dark:bg-gray-700">{s.order}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{s.name}</span>
                <span className={`text-xs ${riskColors[s.risk] ?? ""}`}>{s.risk}</span>
                {!s.reversible && <span className="text-xs text-red-500">irreversible</span>}
              </div>
              {s.description && <p className="text-xs text-gray-400 mt-0.5">{s.description}</p>}
            </div>
            <span className="text-xs text-gray-400">{s.estimated_seconds}s</span>
          </div>
        ))}
      </div>
    </div>
  );
}
