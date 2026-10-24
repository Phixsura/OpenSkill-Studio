"use client";
interface StageResult { stage: string; status: string; }
interface DeployPipePanelProps { stages: StageResult[]; success: boolean; successRate: number; }
const ICON: Record<string, string> = { passed: "✅", failed: "❌", skipped: "⏭️" };
export function DeployPipePanel({ stages, success, successRate }: DeployPipePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Deploy Pipeline</h3>
        <span className={`text-xs font-bold ${success ? "text-green-600" : "text-red-500"}`}>
          {success ? "✅ Passed" : "❌ Failed"} · {successRate}% rate
        </span>
      </div>
      <div className="p-4 flex items-center gap-1">
        {stages.map((s, i) => (
          <div key={s.stage} className="flex items-center gap-1">
            <div className={`px-2 py-1 rounded text-xs ${s.status === "passed" ? "bg-green-100 text-green-700 dark:bg-green-900" : s.status === "failed" ? "bg-red-100 text-red-700 dark:bg-red-900" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
              {ICON[s.status] ?? ""} {s.stage}
            </div>
            {i < stages.length - 1 && <span className="text-gray-400">→</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
