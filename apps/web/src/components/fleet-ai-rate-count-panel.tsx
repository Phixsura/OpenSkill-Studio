"use client";
export function FleetAiRateCountPanel({ counters, active, rps, peakRps, windows }: { counters: number; active: number; rps: number; peakRps: number; windows: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Rate Counter</h3>
    <div className="text-sm">{active}/{counters} active · {rps.toLocaleString()} RPS · peak {peakRps.toLocaleString()} · {windows} windows</div>
  </div>);
}
