"use client";
export function FleetAiStructOutPanel({ services, active, requests, validPct, schemas }: { services: number; active: number; requests: number; validPct: number; schemas: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 AI Structured Output</h3>
    <div className="text-sm">{active}/{services} active · {requests.toLocaleString()} req · {validPct}% valid · {schemas} schemas</div>
  </div>);
}
