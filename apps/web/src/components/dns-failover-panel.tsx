"use client";

interface DnsRecord { domain: string; primary: string; secondary: string; active: string; failoverCount: number; }
interface DnsFailoverPanelProps { records: DnsRecord[]; failedOver: number; }

export function DnsFailoverPanel({ records, failedOver }: DnsFailoverPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 DNS Failover</h3>
        <span className={`text-xs ${failedOver > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {failedOver > 0 ? `⚠ ${failedOver} failed over` : "✅ All primary"} · {records.length} domains
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {records.map(r => (
          <div key={r.domain} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono font-semibold">{r.domain}</span>
              <span className={r.active === "primary" ? "text-green-600" : "text-yellow-600"}>{r.active}</span>
            </div>
            <div className="text-gray-400">P: {r.primary} · S: {r.secondary}{r.failoverCount > 0 ? ` · ${r.failoverCount} failovers` : ""}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
