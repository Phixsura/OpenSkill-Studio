"use client";
export function FleetAiTracingPanel({ tracers, active, traces, spans, avgDepth }: { tracers: number; active: number; traces: number; spans: number; avgDepth: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Tracing</h3>
    <div className="text-sm">{active}/{tracers} active · {traces.toLocaleString()} traces · {spans.toLocaleString()} spans · depth {avgDepth}</div>
  </div>);
}
