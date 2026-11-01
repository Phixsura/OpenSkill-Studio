"use client";

interface StepResult { step: string; status: string; durationMs: number; }
interface OpsRunbookExecProps { runbook: string; results: StepResult[];
  allOk: boolean; stepsExecuted: number; totalSteps: number; totalDurationMs: number; }

export function OpsRunbookExec({ runbook, results, allOk, stepsExecuted, totalSteps, totalDurationMs }: OpsRunbookExecProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">📋 {runbook}</h3>
        <span className={`text-xs ${allOk ? "text-green-600" : "text-red-500"}`}>
          {allOk ? "✅ Complete" : "❌ Failed"} · {stepsExecuted}/{totalSteps} · {totalDurationMs}ms
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span>{r.status === "completed" ? "✅" : "❌"} {r.step}</span>
            <span className="text-gray-400">{r.durationMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
