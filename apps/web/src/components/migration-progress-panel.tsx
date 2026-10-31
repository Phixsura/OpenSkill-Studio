"use client";

interface MigStep { stepId: string; name: string; description: string; status: string; error: string; }
interface MigProgress { status: string; total: number; completed: number; percentage: number; steps: MigStep[]; }

const stepIcons: Record<string, string> = { pending: "⬜", running: "🔄", completed: "✅", failed: "❌", skipped: "⏭️" };

export function MigrationProgressPanel({ progress, onRollback }: { progress: MigProgress; onRollback?: () => void }) {
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <span className="font-bold text-sm">Migration {progress.status}</span>
        {progress.status === "failed" && <button onClick={onRollback} className="text-xs bg-red-500 text-white px-3 py-1 rounded-lg">Rollback</button>}
      </div>
      <div className="h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full">
        <div className={`h-full rounded-full transition-all ${progress.status === "failed" ? "bg-red-500" : "bg-blue-500"}`}
          style={{ width: `${progress.percentage}%` }} />
      </div>
      <span className="text-xs text-gray-500">{progress.completed}/{progress.total} steps ({progress.percentage}%)</span>
      <div className="space-y-1">
        {progress.steps.map(s => (
          <div key={s.stepId} className={`flex items-start gap-2 rounded-lg p-2 text-sm ${s.status === "failed" ? "bg-red-50 dark:bg-red-900/10" : ""}`}>
            <span>{stepIcons[s.status] || "⬜"}</span>
            <div>
              <span className="font-medium">{s.name}</span>
              <span className="text-xs text-gray-500 ml-1">— {s.description}</span>
              {s.error && <span className="text-xs text-red-500 block">{s.error}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
