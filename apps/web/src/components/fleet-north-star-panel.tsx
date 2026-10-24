"use client";
export function FleetNorthStarPanel({ current, target, achievementPct, onTrack }: { current: number; target: number; achievementPct: number; onTrack: boolean; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">⭐ North Star: Weekly Active Devs</h3>
    <div className={`text-3xl font-black ${onTrack ? "text-green-600" : "text-yellow-600"}`}>{current.toLocaleString()}</div>
    <div className="text-xs text-gray-400">Target: {target.toLocaleString()} ({achievementPct}%)</div>
  </div>);
}
