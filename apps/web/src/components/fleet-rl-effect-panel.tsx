"use client";
export function FleetRlEffectPanel({ totalRequests, blocked, falsePositives, precision, effective }: { totalRequests: number; blocked: number; falsePositives: number; precision: number; effective: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 Rate Limiter</h3>
    <div className="text-sm">{blocked.toLocaleString()} blocked · {precision}% precision</div>
    {!effective && <span className="text-xs text-yellow-600">⚠️ {falsePositives} false positives</span>}
  </div>);
}
