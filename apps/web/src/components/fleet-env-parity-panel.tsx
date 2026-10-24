"use client";
export function FleetEnvParityPanel({ total, matching, drifted, parity }: { total: number; matching: number; drifted: number; parity: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Env Parity</h3>
    {parity ? <span className="text-xs text-green-600">✅ All {total} match production</span>
     : <span className="text-xs text-yellow-600">⚠️ {drifted} staging/prod drift</span>}
  </div>);
}
