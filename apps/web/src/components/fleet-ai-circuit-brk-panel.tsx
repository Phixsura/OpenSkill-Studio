"use client";
export function FleetAiCircuitBrkPanel({ breakers, closed, halfOpen, open, trips }: { breakers: number; closed: number; halfOpen: number; open: number; trips: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Circuit Breaker</h3>
    <div className="text-sm">🟢 {closed} closed · 🟡 {halfOpen} half · 🔴 {open} open · {trips} trips/24h</div>
  </div>);
}
