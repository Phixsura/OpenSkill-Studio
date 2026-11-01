"use client";
export function FleetOtelPanel({ total, instrumented, auto, manual, coveragePct, mature }: { total: number; instrumented: number; auto: number; manual: number; coveragePct: number; mature: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 OpenTelemetry</h3>
    <div className={`text-lg font-bold ${mature ? "text-green-600" : "text-yellow-600"}`}>{coveragePct}%</div>
    <div className="text-xs text-gray-400">{auto} auto · {manual} manual · {total - instrumented} uninstrumented</div>
  </div>);
}
