"use client";
interface BackendCircuit { backend: string; trips: number; recoveries: number; requestsBlocked: number; }
interface GwCircuitStatsPanelProps { backends: BackendCircuit[]; totalTrips: number; totalBlocked: number; }
export function GwCircuitStatsPanel({ backends, totalTrips, totalBlocked }: GwCircuitStatsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Gateway Circuits</h3>
        <span className={`text-xs ${totalTrips > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {totalTrips} trips · {totalBlocked} blocked
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {backends.map(b => (
          <div key={b.backend} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{b.backend}</span>
            <span className="text-gray-400">{b.trips} trips · {b.recoveries} recoveries · {b.requestsBlocked} blocked</span>
          </div>
        ))}
      </div>
    </div>
  );
}
