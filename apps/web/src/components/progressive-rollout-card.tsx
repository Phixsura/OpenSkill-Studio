"use client";

interface Stage { name: string; pct: number; duration_hours: number; }
interface ProgressiveRolloutCardProps { stages: Stage[]; currentStage: number; status: string; onAdvance: () => void; onRollback: () => void; }

export function ProgressiveRolloutCard({ stages, currentStage, status, onAdvance, onRollback }: ProgressiveRolloutCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Progressive Rollout</h3>
        <span className={`text-xs font-medium ${status === "completed" ? "text-green-600" : "text-blue-600"}`}>{status}</span>
      </div>
      <div className="mt-3 flex gap-1">
        {stages.map((s, i) => (
          <div key={s.name} className={`h-2 flex-1 rounded ${i <= currentStage ? "bg-blue-500" : "bg-gray-200 dark:bg-gray-700"}`} />
        ))}
      </div>
      <div className="mt-2 flex justify-between text-xs text-gray-400">
        {stages.map((s, i) => <span key={s.name} className={i === currentStage ? "font-bold text-blue-600" : ""}>{s.pct}%</span>)}
      </div>
      {status === "active" && (
        <div className="mt-3 flex justify-end gap-2">
          <button onClick={onRollback} className="rounded border px-2 py-1 text-xs text-red-600">Rollback</button>
          <button onClick={onAdvance} className="rounded bg-blue-600 px-2 py-1 text-xs text-white">Advance</button>
        </div>
      )}
    </div>
  );
}
