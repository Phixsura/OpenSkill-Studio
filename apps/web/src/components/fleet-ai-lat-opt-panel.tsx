"use client";
export function FleetAiLatOptPanel({ services, active, p50, p99, optimizations }: { services: number; active: number; p50: number; p99: number; optimizations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Latency Opt</h3>
    <div className="text-sm">{active}/{services} active · p50 {p50}ms · p99 {p99}ms · {optimizations} opts</div>
  </div>);
}
