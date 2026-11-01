"use client";

interface RunbookStep { step: string; status: string; }
interface RunbookExecPanelProps { name: string; steps: RunbookStep[]; success: boolean; severity: string; }

const STEP_ICON: Record<string, string> = { success: "✅", failed: "❌", skipped: "⏭️" };

export function RunbookExecPanel({ name, steps, success, severity }: RunbookExecPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📖 Runbook: {name}</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{severity}</span>
          <span className={`text-xs font-bold ${success ? "text-green-600" : "text-red-500"}`}>
            {success ? "✅ Done" : "❌ Failed"}
          </span>
        </div>
      </div>
      <div className="p-4 space-y-1">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span>{STEP_ICON[s.status] ?? "⏳"}</span>
            <span className={s.status === "failed" ? "text-red-600" : ""}>{s.step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
