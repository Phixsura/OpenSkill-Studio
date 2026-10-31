"use client";

import { useState } from "react";

interface OutputBlock {
  id: string;
  type: "stdout" | "stderr" | "result" | "metric";
  content: string;
  timestamp: string;
  duration?: number;
}

export function SandboxOutputViewer({
  blocks,
  extensionName,
  executionId,
  totalDuration,
  onRerun,
}: {
  blocks: OutputBlock[];
  extensionName: string;
  executionId: string;
  totalDuration: number;
  onRerun?: () => void;
}) {
  const [filter, setFilter] = useState<string>("all");
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  const filtered = filter === "all" ? blocks : blocks.filter((b) => b.type === filter);

  const typeStyles: Record<string, { bg: string; label: string; icon: string }> = {
    stdout: { bg: "bg-gray-900", label: "stdout", icon: "📤" },
    stderr: { bg: "bg-red-950", label: "stderr", icon: "⚠️" },
    result: { bg: "bg-green-950", label: "result", icon: "✅" },
    metric: { bg: "bg-blue-950", label: "metric", icon: "📊" },
  };

  const stderrCount = blocks.filter((b) => b.type === "stderr").length;

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 flex items-center justify-between">
        <div>
          <h2 className="font-bold text-sm">📋 Execution Output</h2>
          <div className="text-xs text-gray-400">
            {extensionName} · Run {executionId} · {totalDuration}ms
            {stderrCount > 0 && <span className="text-red-400 ml-2">{stderrCount} errors</span>}
          </div>
        </div>
        <div className="flex gap-2">
          {["all", "stdout", "stderr", "result", "metric"].map((f) => (
            <button key={f} onClick={() => setFilter(f)}
              className={`text-xs px-2 py-0.5 rounded ${filter === f ? "bg-blue-600 text-white" : "text-gray-500"}`}>
              {f}
            </button>
          ))}
          {onRerun && (
            <button onClick={onRerun} className="text-xs text-blue-500 border border-blue-300 dark:border-blue-700 px-2 py-0.5 rounded ml-1">
              🔄 Rerun
            </button>
          )}
        </div>
      </div>

      <div className="max-h-80 overflow-y-auto">
        {filtered.map((block) => {
          const style = typeStyles[block.type];
          const isCollapsed = collapsed.has(block.id);
          return (
            <div key={block.id} className={`border-b dark:border-gray-800 ${style.bg}`}>
              <button
                onClick={() => {
                  const next = new Set(collapsed);
                  isCollapsed ? next.delete(block.id) : next.add(block.id);
                  setCollapsed(next);
                }}
                className="w-full text-left px-4 py-1.5 flex items-center justify-between text-xs"
              >
                <span className="text-gray-400">
                  {style.icon} <span className="font-mono">[{style.label}]</span> {block.timestamp}
                  {block.duration !== undefined && <span className="ml-2">{block.duration}ms</span>}
                </span>
                <span className="text-gray-600">{isCollapsed ? "▶" : "▼"}</span>
              </button>
              {!isCollapsed && (
                <pre className="px-4 pb-2 text-xs font-mono text-gray-300 whitespace-pre-wrap overflow-x-auto">
                  {block.content}
                </pre>
              )}
            </div>
          );
        })}
        {filtered.length === 0 && (
          <div className="p-4 text-center text-xs text-gray-500">No output to display</div>
        )}
      </div>
    </div>
  );
}
