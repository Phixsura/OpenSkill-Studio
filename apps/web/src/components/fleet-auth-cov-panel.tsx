"use client";
export function FleetAuthCovPanel({ total, authenticated, publicCount, fullyProtected }: { total: number; authenticated: number; publicCount: number; fullyProtected: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Auth Coverage</h3>
    <div className="text-sm">{authenticated}/{total} authenticated</div>
    {!fullyProtected && <span className="text-xs text-yellow-600">⚠️ {publicCount} public endpoints</span>}
  </div>);
}
