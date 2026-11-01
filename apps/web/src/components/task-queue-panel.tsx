"use client";

import { useState } from "react";

interface QueueTask {
  taskId: string;
  name: string;
  state: "pending" | "running" | "completed" | "failed" | "cancelled" | "waiting";
  priority: number;
  progress: number;
  retryCount: number;
  maxRetries: number;
  error?: string;
  dependsOn?: string;
}

interface QueueStats {
  total: number;
  byState: Record<string, number>;
}

const stateConfig: Record<string, { color: string; icon: string }> = {
  pending: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "⏳" },
  running: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "▶" },
  completed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
  cancelled: { color: "bg-gray-200 text-gray-500 dark:bg-gray-800", icon: "⊘" },
  waiting: { color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30", icon: "⏸" },
};

export function TaskQueuePanel({
  tasks,
  stats,
  onCancel,
  onRetry,
}: {
  tasks: QueueTask[];
  stats: QueueStats;
  onCancel?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
}) {
  const [filter, setFilter] = useState<string>("all");
  const filtered = filter === "all" ? tasks : tasks.filter((t) => t.state === filter);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📋 Task Queue</h2>

      <div className="flex gap-2 flex-wrap text-xs">
        {["all", "pending", "running", "waiting", "completed", "failed"].map((s) => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-2.5 py-1 rounded-full ${filter === s ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {s} ({s === "all" ? stats.total : stats.byState[s] || 0})
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((task) => {
          const cfg = stateConfig[task.state];
          return (
            <div key={task.taskId} className="rounded-lg border dark:border-gray-700 p-3">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-semibold text-sm">{task.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{task.state}</span>
                  {task.priority > 0 && <span className="text-xs text-gray-400">P{task.priority}</span>}
                  {task.dependsOn && <span className="text-xs text-purple-500">⛓ {task.dependsOn}</span>}
                </div>
                <div className="flex gap-1">
                  {task.state === "pending" && (
                    <button onClick={() => onCancel?.(task.taskId)}
                      className="text-xs text-red-500">Cancel</button>
                  )}
                  {task.state === "failed" && (
                    <button onClick={() => onRetry?.(task.taskId)}
                      className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">Retry</button>
                  )}
                </div>
              </div>
              {task.state === "running" && (
                <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${task.progress}%` }} />
                </div>
              )}
              {task.error && <div className="text-xs text-red-500 mt-1">{task.error}</div>}
              {task.retryCount > 0 && <span className="text-xs text-gray-400">retries: {task.retryCount}/{task.maxRetries}</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
