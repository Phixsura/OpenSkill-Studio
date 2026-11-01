"use client";
export function FleetAiMarketV7Panel({ trackers, active, share, tam, competitors, winRate }: { trackers: number; active: number; share: number; tam: number; competitors: number; winRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Market v7</h3>
    <div className="text-sm">{active}/{trackers} active · {share}% share · ${tam.toLocaleString()} TAM · {competitors} competitors · {winRate}% win</div>
  </div>);
}
