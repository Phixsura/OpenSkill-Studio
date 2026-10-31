"use client";
export function FleetCircuitResPanel({ total, closed, trips, avgRecovery, resilient }: { total: number; closed: number; trips: number; avgRecovery: number; resilient: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Circuit Resilience</h3>
    <div className="text-sm">{closed}/{total} closed · {trips} trips/24h · {avgRecovery}s recovery</div>
    {resilient && <span className="text-xs text-green-600">✅ Resilient</span>}
  </div>);
}
