"use client";
export function FleetLoadtestPanel({ total, passed, maxRps, avgP99, allPassed }: { total: number; passed: number; maxRps: number; avgP99: number; allPassed: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏋️ Load Tests</h3>
    <div className="text-sm">{passed}/{total} passed · peak {maxRps.toLocaleString()} rps · p99 {avgP99}ms</div>
    {!allPassed && <span className="text-xs text-red-500">⚠️ Some tests failed</span>}
  </div>);
}
