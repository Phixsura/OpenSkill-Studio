"use client";

interface DnsCheck { type: string; name: string; expected: string; resolved: boolean; }
interface DnsHealthPanelProps { domain: string; checks: DnsCheck[];
  allOk: boolean; propagationPct: number; }

export function DnsHealthPanel({ domain, checks, allOk, propagationPct }: DnsHealthPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">🌐 DNS: {domain}</h3>
        <div className="flex gap-2 text-xs">
          <span className={allOk ? "text-green-600" : "text-red-500"}>{allOk ? "✅ All OK" : "⚠ Issues"}</span>
          <span className="text-gray-400">{propagationPct}% propagated</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map((c, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{c.resolved ? "✅" : "❌"}</span>
              <span className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded font-mono">{c.type}</span>
              <span className="font-mono text-gray-400">{c.expected || "—"}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
