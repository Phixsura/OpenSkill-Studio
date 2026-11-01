"use client";
export function FleetGitopsSyncV9Panel({ repos, synced }: { repos: number; synced: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 GitOps Sync v9</h3>
    <div className="text-sm">{repos} repos · {synced} synced</div>
  </div>);
}
