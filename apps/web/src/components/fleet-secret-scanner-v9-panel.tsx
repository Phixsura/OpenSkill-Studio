"use client";
export function FleetSecretScannerV9Panel({ repos, secretsFound }: { repos: number; secretsFound: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Secret Scanner v9</h3>
    <div className="text-sm">{repos} repos · {secretsFound} secrets found</div>
  </div>);
}
