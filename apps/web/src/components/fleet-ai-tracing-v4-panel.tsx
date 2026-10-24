"use client";
export function FleetAiTracingV4Panel({ systems, active, traces, spans, sampling }: { systems: number; active: number; traces: number; spans: number; sampling: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Tracing v4</h3>
    <div className="text-sm">{active}/{systems} active · {traces.toLocaleString()} traces · {spans.toLocaleString()} spans · {sampling}% sample</div>
  </div>);
}
