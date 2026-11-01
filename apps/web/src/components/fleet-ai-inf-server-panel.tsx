"use client";
export function FleetAiInfServerPanel({ servers, healthy, rps, ttft, tps }: { servers: number; healthy: number; rps: number; ttft: number; tps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ AI Inference Server</h3>
    <div className="text-sm">{healthy}/{servers} healthy · {rps.toLocaleString()} RPS · TTFT {ttft}ms · {tps} tok/s</div>
  </div>);
}
