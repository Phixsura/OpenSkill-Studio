"use client";

import { useState } from "react";

interface SpanNode {
  spanId: string;
  name: string;
  durationMs: number;
  status: "ok" | "error";
  children: SpanNode[];
}

interface SpanFlat {
  spanId: string;
  name: string;
  durationMs: number;
  status: string;
  parentId: string;
  eventCount: number;
}

export function TraceViewerPanel({
  tree,
  spans,
  traceId,
  totalDurationMs,
}: {
  tree: SpanNode | null;
  spans: SpanFlat[];
  traceId: string;
  totalDurationMs: number;
}) {
  const [view, setView] = useState<"tree" | "list">("tree");
  const errorCount = spans.filter((s) => s.status === "error").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔍 Trace Viewer</h2>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <code>{traceId}</code>
          <span>{totalDurationMs}ms</span>
          <span>{spans.length} spans</span>
          {errorCount > 0 && <span className="text-red-500">{errorCount} errors</span>}
        </div>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setView("tree")}
          className={`text-xs px-3 py-1 rounded-lg ${view === "tree" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Tree
        </button>
        <button onClick={() => setView("list")}
          className={`text-xs px-3 py-1 rounded-lg ${view === "list" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Flat List
        </button>
      </div>

      {view === "tree" && tree && <SpanTree node={tree} maxDuration={totalDurationMs} depth={0} />}

      {view === "list" && (
        <div className="space-y-1">
          {spans.map((s) => (
            <div key={s.spanId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${s.status === "error" ? "bg-red-500" : "bg-green-500"}`} />
                <span className="text-sm">{s.name}</span>
                {s.eventCount > 0 && <span className="text-xs text-gray-400">{s.eventCount} events</span>}
              </div>
              <span className="text-xs font-mono text-gray-500">{s.durationMs}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SpanTree({ node, maxDuration, depth }: { node: SpanNode; maxDuration: number; depth: number }) {
  const widthPct = maxDuration > 0 ? Math.max((node.durationMs / maxDuration) * 100, 5) : 100;
  return (
    <div className="space-y-1" style={{ paddingLeft: depth > 0 ? 16 : 0 }}>
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full shrink-0 ${node.status === "error" ? "bg-red-500" : "bg-green-500"}`} />
        <span className="text-sm shrink-0">{node.name}</span>
        <div className="flex-1 h-4 bg-gray-100 dark:bg-gray-800 rounded overflow-hidden">
          <div className={`h-full rounded ${node.status === "error" ? "bg-red-400" : "bg-blue-400"}`}
            style={{ width: `${widthPct}%` }} />
        </div>
        <span className="text-xs font-mono text-gray-500 shrink-0">{node.durationMs}ms</span>
      </div>
      {node.children.map((child) => (
        <SpanTree key={child.spanId} node={child} maxDuration={maxDuration} depth={depth + 1} />
      ))}
    </div>
  );
}
