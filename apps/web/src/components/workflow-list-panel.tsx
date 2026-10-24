"use client";

interface WorkflowInfo { id: string; name: string; trigger: string; enabled: boolean;
  steps: number; runs: number; lastStatus: string | null; }
interface WorkflowListPanelProps { workflows: WorkflowInfo[];
  onToggle: (id: string) => void; onRun: (id: string) => void; }

const TRIGGER_ICON: Record<string, string> = {
  push_to_main: "🔀", manual: "👆", schedule: "⏰", webhook: "🔗",
};

export function WorkflowListPanel({ workflows, onToggle, onRun }: WorkflowListPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">⚙️ Workflows</h3>
      <div className="space-y-2">
        {workflows.map(w => (
          <div key={w.id} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <span>{TRIGGER_ICON[w.trigger] || "📌"}</span>
                <span className="text-sm font-medium">{w.name}</span>
                <span className="text-xs text-gray-400">{w.steps} steps · {w.runs} runs</span>
              </div>
              {w.lastStatus && (
                <span className={`text-xs ml-6 ${w.lastStatus === "success" ? "text-green-600" : "text-red-500"}`}>
                  Last: {w.lastStatus}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {w.enabled && (
                <button onClick={() => onRun(w.id)}
                  className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Run</button>
              )}
              <button onClick={() => onToggle(w.id)}
                className={`w-8 h-4 rounded-full ${w.enabled ? "bg-green-500" : "bg-gray-300"}`}>
                <span className={`block w-3 h-3 rounded-full bg-white transform ${w.enabled ? "translate-x-4" : "translate-x-0.5"}`} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
