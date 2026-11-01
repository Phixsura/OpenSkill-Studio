"use client";
export function FleetGitMirrorV9Panel({ mirrors, synced }: { mirrors: number; synced: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪞 Git Mirror v9</h3>
    <div className="text-sm">{mirrors} mirrors · {synced} synced</div>
  </div>);
}
