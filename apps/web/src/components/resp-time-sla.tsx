"use client";

interface SlaResult { endpoint: string; p99Ms: number; targetMs: number; withinSla: boolean; marginMs: number; }
interface RespTimeSlaPanelProps { results: SlaResult[]; slaPct: number; met: number; breached: number; }

export function RespTimeSlaPanel({ results, slaPct, met, breached }: RespTimeSlaPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Response Time SLA</h3>
        <span className={`text-xs ${slaPct === 100 ? "text-green-600" : "text-yellow-600"}`}>
          {slaPct}% · {met} met / {breached} breached
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.endpoint} className="flex justify-between px-4 py-2 text-xs">
            <span className={r.withinSla ? "" : "text-red-600 font-bold"}>{r.withinSla ? "✅" : "❌"} {r.endpoint}</span>
            <span className="font-mono">{r.p99Ms}ms / {r.targetMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
