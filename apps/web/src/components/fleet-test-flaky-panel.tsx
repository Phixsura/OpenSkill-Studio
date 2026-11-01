"use client";
export function FleetTestFlakyPanel({ total, flaky, flakyRate, acceptable }: { total: number; flaky: number; flakyRate: number; acceptable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎲 Test Flakiness</h3>
    <div className="text-sm">{flaky}/{total} flaky ({flakyRate}%)</div>
    {!acceptable && <span className="text-xs text-red-500">⚠️ Too many flaky tests</span>}
  </div>);
}
