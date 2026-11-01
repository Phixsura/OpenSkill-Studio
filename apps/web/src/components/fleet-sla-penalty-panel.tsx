"use client";
export function FleetSlaPenaltyPanel({ breaches, totalPenalty, clean }: { breaches: number; totalPenalty: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ SLA Penalties</h3>
    {clean ? <span className="text-xs text-green-600">✅ No breaches</span>
     : <span className="text-xs text-red-500">💸 {breaches} breaches · ${totalPenalty.toLocaleString()}</span>}
  </div>);
}
