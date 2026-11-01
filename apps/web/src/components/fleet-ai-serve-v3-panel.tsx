"use client";
export function FleetAiServeV3Panel({ servers, active, models, rps, p99, gpuUtil }: { servers: number; active: number; models: number; rps: number; p99: number; gpuUtil: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Serving v3</h3>
    <div className="text-sm">{active}/{servers} active · {models} models · {rps.toLocaleString()} RPS · p99 {p99}ms · GPU {gpuUtil}%</div>
  </div>);
}
