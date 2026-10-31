"use client";
export function FleetAiLeadershipV7Panel({ trackers, active, rank, awards, rating }: { trackers: number; active: number; rank: number; awards: number; rating: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👑 AI Leadership v7</h3>
    <div className="text-sm">{active}/{trackers} active · #{rank} market · {awards} awards · ⭐ {rating}</div>
  </div>);
}
