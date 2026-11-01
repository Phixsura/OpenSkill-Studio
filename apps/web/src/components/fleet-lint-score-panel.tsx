"use client";
export function FleetLintScorePanel({ totalRepos, clean, totalErrors, cleanPct }: { totalRepos: number; clean: number; totalErrors: number; cleanPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧹 Lint Score</h3>
    <div className="text-sm">{clean}/{totalRepos} clean ({cleanPct}%) · {totalErrors} errors</div>
  </div>);
}
