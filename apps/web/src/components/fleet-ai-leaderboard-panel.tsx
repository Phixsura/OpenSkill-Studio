"use client";
export function FleetAiLeaderboardPanel({ boards, active, models, benchmarks, submissions }: { boards: number; active: number; models: number; benchmarks: number; submissions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏆 AI Leaderboard</h3>
    <div className="text-sm">{active}/{boards} active · {models} models · {benchmarks} benchmarks · {submissions.toLocaleString()} submissions</div>
  </div>);
}
