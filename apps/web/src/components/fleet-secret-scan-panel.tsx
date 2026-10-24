"use client";
export function FleetSecretScanPanel({ totalRepos, clean, leaked, allClean }: { totalRepos: number; clean: number; leaked: number; allClean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Secret Scanning</h3>
    {allClean ? <span className="text-xs text-green-600">✅ All {totalRepos} repos clean</span>
     : <span className="text-xs text-red-500">🚨 {leaked} secrets found!</span>}
  </div>);
}
