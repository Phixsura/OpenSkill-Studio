"use client";

import { useState } from "react";

interface PipelineStage {
  name: string;
  stageType: string;
  status: "pending" | "running" | "completed" | "failed";
  recordsIn: number;
  recordsOut: number;
  durationMs: number;
  error?: string;
}

interface DataPipeline {
  id: string;
  name: string;
  status: "idle" | "running" | "completed" | "failed" | "paused";
  stages: PipelineStage[];
  totalRecords: number;
  runCount: number;
  lastDurationMs: number;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  idle: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "⏸" },
  running: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "▶" },
  completed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
  paused: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⏸" },
  pending: { color: "bg-gray-100 text-gray-500 dark:bg-gray-800", icon: "⏳" },
};

const stageTypeColors: Record<string, string> = {
  extract: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  transform: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
  load: "bg-green-100 text-green-700 dark:bg-green-900/30",
  validate: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  filter: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
};

export function DataPipelinePanel({
  pipelines,
  onRun,
}: {
  pipelines: DataPipeline[];
  onRun?: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔀 Data Pipelines</h2>

      <div className="space-y-2">
        {pipelines.map((p) => {
          const cfg = statusConfig[p.status];
          return (
            <div key={p.id} className="rounded-xl border dark:border-gray-700 overflow-hidden">
              <div className="flex items-center justify-between p-3 cursor-pointer"
                onClick={() => setExpanded(expanded === p.id ? null : p.id)}>
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-semibold text-sm">{p.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{p.status}</span>
                  <span className="text-xs text-gray-400">{p.stages.length} stages</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">×{p.runCount}</span>
                  {p.lastDurationMs > 0 && <span className="text-xs text-gray-400">{p.lastDurationMs}ms</span>}
                  {p.status !== "running" && (
                    <button onClick={(e) => { e.stopPropagation(); onRun?.(p.id); }}
                      className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Run</button>
                  )}
                </div>
              </div>

              {expanded === p.id && (
                <div className="border-t dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-1">
                  {p.stages.map((stage, i) => {
                    const sCfg = statusConfig[stage.status] || statusConfig.pending;
                    return (
                      <div key={i} className="flex items-center gap-2 text-xs">
                        <span className="w-4">{sCfg.icon}</span>
                        <span className={`px-1.5 py-0.5 rounded ${stageTypeColors[stage.stageType] || "bg-gray-100"}`}>
                          {stage.stageType}
                        </span>
                        <span className="font-medium">{stage.name}</span>
                        {stage.status === "completed" && (
                          <span className="text-gray-400">{stage.recordsIn}→{stage.recordsOut}</span>
                        )}
                        {stage.error && <span className="text-red-500">{stage.error}</span>}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
