"use client";
export function FleetAiObsPanel({ instances, active, traces, spans }: { instances: number; active: number; traces: number; spans: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ AI Observability</h3>
    <div className="text-sm">{active}/{instances} active · {traces.toLocaleString()} traces · {spans.toLocaleString()} spans</div>
  </div>);
}
