"use client";
export function FleetDnsPanel({ avgMs, failures, healthy }: { avgMs: number; failures: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 Fleet DNS</h3>
    <div className="text-sm">Avg {avgMs}ms · {failures} failures</div>
    <span className={`text-xs ${healthy ? "text-green-600" : "text-red-500"}`}>{healthy ? "✅ Healthy" : "❌ Issues"}</span>
  </div>);
}
