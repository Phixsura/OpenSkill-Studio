"use client";
export function FleetIncLearnPanel({ total, implemented, pending, learningRate }: { total: number; implemented: number; pending: number; learningRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 Incident Learning</h3>
    <div className="text-sm">{implemented}/{total} implemented ({learningRate}%)</div>
    {pending > 0 && <span className="text-xs text-yellow-600">⏳ {pending} lessons pending</span>}
  </div>);
}
