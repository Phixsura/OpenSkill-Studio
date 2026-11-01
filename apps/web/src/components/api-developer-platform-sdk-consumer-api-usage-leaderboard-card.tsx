"use client";

import { useState } from "react";

interface RankEntry {
  rank: number;
  consumerId: string;
  points: number;
  tier: string;
  badges: number;
}

const TIER_COLOR: Record<string, string> = {
  bronze: "text-amber-700 dark:text-amber-400",
  silver: "text-zinc-500 dark:text-zinc-300",
  gold: "text-yellow-600 dark:text-yellow-400",
  platinum: "text-cyan-600 dark:text-cyan-400",
  diamond: "text-purple-600 dark:text-purple-400",
};

export default function UsageLeaderboardCard() {
  const [ranking] = useState<RankEntry[]>([
    { rank: 1, consumerId: "acme-corp", points: 125000, tier: "platinum", badges: 5 },
    { rank: 2, consumerId: "beta-inc", points: 45000, tier: "gold", badges: 3 },
    { rank: 3, consumerId: "gamma-labs", points: 12000, tier: "gold", badges: 2 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Usage Leaderboard</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Ranked consumer usage with gamification</p>

      <div className="mt-4 space-y-2">
        {ranking.map((r) => (
          <div key={r.consumerId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-zinc-100 text-xs font-bold text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                {r.rank}
              </span>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{r.consumerId}</span>
              <span className={`text-xs font-semibold ${TIER_COLOR[r.tier] ?? ""}`}>{r.tier}</span>
            </div>
            <div className="text-xs text-zinc-500">
              {r.points.toLocaleString()} pts · {r.badges} 🏅
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        Top {ranking.length} consumers
      </div>
    </div>
  );
}
