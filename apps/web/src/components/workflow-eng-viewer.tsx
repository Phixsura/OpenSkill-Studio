"use client";

interface StepResult { step: string; status: string; }
interface WorkflowEngViewerProps { name: string; steps: StepResult[]; success: boolean; }

const STEP_ICON: Record<string, string> = { success: "✅", failed: "❌", pending: "⏳" };

export function WorkflowEngViewer({ name, steps, success }: WorkflowEngViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Workflow: {name}</h3>
        <span className={`text-xs font-bold ${success ? "text-green-600" : "text-red-500"}`}>
          {success ? "✅ Complete" : "❌ Failed"}
        </span>
      </div>
      <div className="p-4 space-y-2">
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
