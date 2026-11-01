"use client";
export function FleetAiLoadTestPanel({ testers, active, tests, maxRps, p99, errorPct }: { testers: number; active: number; tests: number; maxRps: number; p99: number; errorPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏋️ AI Load Test</h3>
    <div className="text-sm">{active}/{testers} active · {tests} tests · {maxRps.toLocaleString()} max RPS · p99 {p99}ms · {errorPct}% err</div>
  </div>);
}
