"use client";
export function FleetAiTelemetryPanel({ collectors, active, spans, tokens, cost }: { collectors: number; active: number; spans: number; tokens: number; cost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Telemetry</h3>
    <div className="text-sm">{active}/{collectors} active · {spans.toLocaleString()} spans · ${cost.toLocaleString()} tracked</div>
  </div>);
}
