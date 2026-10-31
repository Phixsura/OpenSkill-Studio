"use client";
export function FleetAiCbV2Panel({ breakers, active, closed, halfOpen, open, trips }: { breakers: number; active: number; closed: number; halfOpen: number; open: number; trips: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Circuit Breaker v2</h3>
    <div className="text-sm">🟢 {closed} · 🟡 {halfOpen} · 🔴 {open} of {breakers} · {trips} trips</div>
  </div>);
}
