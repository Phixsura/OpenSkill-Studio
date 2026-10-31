"use client";
export function FleetAiGitopsPanel({ controllers, active, repos, syncs, outOfSync }: { controllers: number; active: number; repos: number; syncs: number; outOfSync: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI GitOps</h3>
    <div className="text-sm">{active}/{controllers} active · {repos} repos · {syncs} syncs · {outOfSync} out-of-sync</div>
  </div>);
}
