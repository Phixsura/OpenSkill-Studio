"use client";
export function FleetAiSecretScanPanel({ scanners, active, repos, found, revoked }: { scanners: number; active: number; repos: number; found: number; revoked: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 AI Secret Scanner</h3>
    <div className="text-sm">{active}/{scanners} active · {repos} repos · {found} found · {revoked} revoked</div>
  </div>);
}
