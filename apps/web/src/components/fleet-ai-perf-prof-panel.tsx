"use client";
export function FleetAiPerfProfPanel({ profilers, active, profiles, bottlenecks, optimizations }: { profilers: number; active: number; profiles: number; bottlenecks: number; optimizations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 AI Perf Profiler</h3>
    <div className="text-sm">{active}/{profilers} active · {profiles.toLocaleString()} profiles · {bottlenecks} bottlenecks · {optimizations} optimizations</div>
  </div>);
}
