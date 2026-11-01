"use client";
export function FleetLightstepPanel({ total, instrumented, latencyRegressions, coveragePct }: { total: number; instrumented: number; latencyRegressions: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💡 Lightstep</h3>
    <div className="text-sm">{instrumented}/{total} instrumented ({coveragePct}%)</div>
    {latencyRegressions > 0 && <span className="text-xs text-yellow-600">⚠️ {latencyRegressions} latency regressions</span>}
  </div>);
}
