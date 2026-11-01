"use client";
export function FleetAiCompetitiveV7Panel({ trackers, active, competitors, winRate, share, ahead }: { trackers: number; active: number; competitors: number; winRate: number; share: number; ahead: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚔️ AI Competitive v7</h3>
    <div className="text-sm">{active}/{trackers} active · {competitors} competitors · {winRate}% win · {share}% share · {ahead} features ahead</div>
  </div>);
}
