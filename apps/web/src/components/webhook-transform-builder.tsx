"use client";

import { useState } from "react";

interface TransformStep {
  operation: string;
  config: Record<string, unknown>;
}

interface TransformPipeline {
  id: string;
  name: string;
  eventType: string;
  steps: TransformStep[];
  enabled: boolean;
  executionCount: number;
}

const opIcons: Record<string, string> = {
  map: "🔀", filter: "🔍", enrich: "➕", template: "📝",
  flatten: "📋", wrap: "📦",
};

const opColors: Record<string, string> = {
  map: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  filter: "bg-green-100 text-green-700 dark:bg-green-900/30",
  enrich: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
  template: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  flatten: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
  wrap: "bg-pink-100 text-pink-700 dark:bg-pink-900/30",
};

export function WebhookTransformBuilder({
  pipelines,
  onToggle,
  onDelete,
  onTest,
}: {
  pipelines: TransformPipeline[];
  onToggle?: (id: string) => void;
  onDelete?: (id: string) => void;
  onTest?: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔧 Webhook Transforms</h2>

      <div className="space-y-2">
        {pipelines.map((p) => (
          <div key={p.id} className={`rounded-xl border dark:border-gray-700 overflow-hidden ${!p.enabled ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between p-3 cursor-pointer"
              onClick={() => setExpanded(expanded === p.id ? null : p.id)}>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{p.name}</span>
                <span className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{p.eventType}</span>
                <span className="text-xs text-gray-400">{p.steps.length} steps</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">×{p.executionCount}</span>
                <button onClick={(e) => { e.stopPropagation(); onTest?.(p.id); }}
                  className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">Test</button>
                <button onClick={(e) => { e.stopPropagation(); onToggle?.(p.id); }}
                  className={`text-xs px-2 py-0.5 rounded ${p.enabled ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                  {p.enabled ? "On" : "Off"}
                </button>
                <button onClick={(e) => { e.stopPropagation(); onDelete?.(p.id); }}
                  className="text-xs text-red-500">✕</button>
              </div>
            </div>

            {expanded === p.id && (
              <div className="border-t dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50">
                <div className="flex items-center gap-1">
                  {p.steps.map((step, i) => (
                    <div key={i} className="flex items-center gap-1">
                      {i > 0 && <span className="text-gray-400">→</span>}
                      <span className={`text-xs px-2 py-1 rounded ${opColors[step.operation] || "bg-gray-100"}`}>
                        {opIcons[step.operation] || "⚙"} {step.operation}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
