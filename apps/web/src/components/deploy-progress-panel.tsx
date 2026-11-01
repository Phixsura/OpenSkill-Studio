"use client";
interface Step { name: string; status: string; }
interface DeployProgressPanelProps { deployId: string; steps: Step[]; progressPct: number; status: string; }
const STEP_ICON: Record<string, string> = { completed: "✅", failed: "❌", pending: "⏳", in_progress: "🔄" };
export function DeployProgressPanel({ deployId, steps, progressPct, status }: DeployProgressPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Deploy: {deployId}</h3>
        <span className={`text-xs font-bold ${status === "completed" ? "text-green-600" : status === "failed" ? "text-red-500" : "text-blue-500"}`}>
          {progressPct}% · {status}
        </span>
      </div>
      <div className="p-4">
        <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full mb-3">
          <div className={`h-full rounded-full ${status === "failed" ? "bg-red-500" : "bg-green-500"}`}
            style={{ width: `${progressPct}%` }} />
        </div>
        <div className="space-y-1">
          {steps.map(s => (
            <div key={s.name} className="flex items-center gap-2 text-xs">
              <span>{STEP_ICON[s.status] ?? "⏳"}</span>
              <span className={s.status === "failed" ? "text-red-600" : ""}>{s.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
