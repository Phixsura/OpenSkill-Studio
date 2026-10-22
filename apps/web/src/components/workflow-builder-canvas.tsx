"use client";

interface WorkflowStep { type: "trigger" | "action"; config: Record<string, unknown>; }
interface WorkflowBuilderCanvasProps { steps: WorkflowStep[]; onAddAction: () => void; onRemoveStep: (index: number) => void; }

export function WorkflowBuilderCanvas({ steps, onAddAction, onRemoveStep }: WorkflowBuilderCanvasProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Workflow Builder</h3>
      <div className="mt-4 space-y-2">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            {i > 0 && <div className="mx-auto h-4 w-px bg-gray-300 dark:bg-gray-600" />}
            <div className={`flex flex-1 items-center justify-between rounded-lg border p-3 ${s.type === "trigger" ? "border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-900/20" : "border-gray-200 dark:border-gray-700"}`}>
              <span className="text-sm font-medium">{s.type === "trigger" ? "⚡ Trigger" : `🔧 Action ${i}`}</span>
              {s.type !== "trigger" && (
                <button onClick={() => onRemoveStep(i)} className="text-xs text-red-500">Remove</button>
              )}
            </div>
          </div>
        ))}
      </div>
      <button onClick={onAddAction} className="mt-3 w-full rounded border border-dashed border-gray-300 py-2 text-sm text-gray-500 hover:bg-gray-50 dark:border-gray-600">
        + Add Action
      </button>
    </div>
  );
}
