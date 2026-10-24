"use client";

interface DnsRecord { domain: string; type: string; resolved: boolean; ttl: number; ip: string; }
interface DnsHealthPanelProps { records: DnsRecord[]; healthy: number; unhealthy: number; allHealthy: boolean; }

export function DnsHealthPanel({ records, healthy, unhealthy, allHealthy }: DnsHealthPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 DNS Health</h3>
        <span className={`text-xs ${allHealthy ? "text-green-600" : "text-red-500"}`}>
          {allHealthy ? `✅ ${healthy} healthy` : `⚠ ${unhealthy} unhealthy`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {records.map(r => (
          <div key={r.domain} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${r.resolved ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono">{r.domain}</span>
            </div>
            <span className="text-gray-400">{r.type} · {r.ip || "unresolved"} · TTL {r.ttl}s</span>
          </div>
        ))}
      </div>
    </div>
  );
}
