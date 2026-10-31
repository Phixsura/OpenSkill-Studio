"use client";

interface Step { step: number; type: string; label: string; }
interface Trigger { type: string; label: string; }
interface WorkflowBuilderCanvasProps { name: string; trigger: Trigger; steps: Step[];
  status: string; onAddStep: () => void; onActivate: () => void; }

const stepIcon: Record<string, string> = {
  http_request: "🌐", send_email: "📧", transform: "🔄",
  condition: "🔀", delay: "⏳", notify: "🔔",
};

export function WorkflowBuilderCanvas({ name, trigger, steps, status, onAddStep, onActivate }: WorkflowBuilderCanvasProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{name}</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs ${status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
          {status}
        </span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <div className="rounded-lg border-2 border-blue-400 bg-blue-50 px-4 py-2 text-center dark:bg-blue-900/10">
          <p className="text-xs text-gray-400">Trigger</p>
          <p className="text-sm font-medium">{trigger.label}</p>
        </div>
        {steps.map(s => (
          <div key={s.step}>
            <div className="mx-auto h-4 w-px bg-gray-300 dark:bg-gray-600" />
            <div className="rounded-lg border px-4 py-2 text-center dark:border-gray-700">
              <span className="text-lg">{stepIcon[s.type] ?? "⚙️"}</span>
              <p className="text-sm">{s.label}</p>
            </div>
          </div>
        ))}
        <button onClick={onAddStep} className="rounded border border-dashed px-4 py-1.5 text-xs text-gray-400 dark:border-gray-600">
          + Add Step
        </button>
      </div>
      <button onClick={onActivate} disabled={status === "active"}
        className="w-full rounded bg-green-600 py-2 text-sm text-white disabled:opacity-50">
        {status === "active" ? "Active" : "Activate Workflow"}
      </button>
    </div>
  );
}
