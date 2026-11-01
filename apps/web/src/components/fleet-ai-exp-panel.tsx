"use client";
export function FleetAiExpPanel({ total, active, variants, avgTraffic }: { total: number; active: number; variants: number; avgTraffic: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 AI Experiments</h3>
    <div className="text-sm">{active}/{total} active · {variants} variants · {avgTraffic}% traffic</div>
  </div>);
}
