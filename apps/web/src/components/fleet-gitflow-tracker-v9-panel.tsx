"use client";
export function FleetGitflowTrackerV9Panel({ repos, openPrs }: { repos: number; openPrs: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌿 Gitflow Tracker v9</h3>
    <div className="text-sm">{repos} repos · {openPrs} open PRs</div>
  </div>);
}
