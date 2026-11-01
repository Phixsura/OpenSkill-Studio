"use client";

interface DnsResult { domain: string; resolved: boolean; latencyMs: number; healthy: boolean; }
interface DnsMonitorPanelProps { results: DnsResult[]; healthy: number; total: number; allHealthy: boolean; }

export function DnsMonitorPanel({ results, healthy, total, allHealthy }: DnsMonitorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 DNS Monitor</h3>
        <span className={`text-xs ${allHealthy ? "text-green-600" : "text-red-500"}`}>
          {healthy}/{total} healthy
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.domain} className="flex items-center justify-between px-4 py-2 text-xs">
            <span>{r.healthy ? "🟢" : "🔴"} {r.domain}</span>
            <span className="text-gray-400">{r.resolved ? `${r.latencyMs}ms` : "unresolved"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
