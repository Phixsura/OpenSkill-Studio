"use client";

interface WorkflowRun {
  id: string;
  name: string;
  trigger: string;
  status: "running" | "completed" | "failed" | "canceled" | "queued";
  startedAt: string;
  duration: string;
  steps: { name: string; status: "passed" | "failed" | "running" | "skipped" | "queued" }[];
}

export function WorkflowStatusPanel({
  runs,
  onCancel,
  onRetry,
}: {
  runs: WorkflowRun[];
  onCancel?: (id: string) => void;
  onRetry?: (id: string) => void;
}) {
  const statusConfig: Record<string, { icon: string; color: string }> = {
    running: { icon: "⏳", color: "text-blue-500" },
    completed: { icon: "✅", color: "text-green-500" },
    failed: { icon: "❌", color: "text-red-500" },
    canceled: { icon: "⛔", color: "text-gray-400" },
    queued: { icon: "📋", color: "text-yellow-500" },
  };

  const stepIcons: Record<string, string> = {
    passed: "✅", failed: "❌", running: "⏳", skipped: "⏭️", queued: "⬜",
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">⚙️ Workflow Runs</h2>

      <div className="space-y-3">
        {runs.map((run) => {
          const cfg = statusConfig[run.status];
          return (
            <div key={run.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={cfg.color}>{cfg.icon}</span>
                  <span className="font-semibold text-sm">{run.name}</span>
                  <span className="text-xs text-gray-400">via {run.trigger}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <span>{run.startedAt}</span>
                  <span>· {run.duration}</span>
                  {run.status === "running" && onCancel && (
                    <button onClick={() => onCancel(run.id)}
                      className="text-red-400 border border-red-300 dark:border-red-700 px-2 py-0.5 rounded">
                      Cancel
                    </button>
                  )}
                  {run.status === "failed" && onRetry && (
                    <button onClick={() => onRetry(run.id)}
                      className="text-blue-400 border border-blue-300 dark:border-blue-700 px-2 py-0.5 rounded">
                      Retry
                    </button>
                  )}
                </div>
              </div>

              {/* Step progress */}
              <div className="flex gap-1">
                {run.steps.map((step, i) => (
                  <div key={i} className="flex-1 group relative">
                    <div className={`h-2 rounded-full ${
                      step.status === "passed" ? "bg-green-500" :
                      step.status === "failed" ? "bg-red-500" :
                      step.status === "running" ? "bg-blue-500 animate-pulse" :
                      step.status === "skipped" ? "bg-gray-300 dark:bg-gray-600" :
                      "bg-gray-200 dark:bg-gray-700"
                    }`} />
                    <div className="text-center text-xs mt-1">
                      <span>{stepIcons[step.status]}</span>
                      <div className="text-gray-400 truncate">{step.name}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
