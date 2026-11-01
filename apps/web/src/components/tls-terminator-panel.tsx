"use client";
interface TlsCert { domain: string; expiresDays: number; active: boolean; }
interface TlsTerminatorPanelProps { certs: TlsCert[]; totalConnections: number; expiringSoon: number; }
export function TlsTerminatorPanel({ certs, totalConnections, expiringSoon }: TlsTerminatorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 TLS Termination</h3>
        <span className="text-xs text-gray-400">
          {certs.length} certs · {totalConnections.toLocaleString()} conn{expiringSoon > 0 ? ` · ⚠ ${expiringSoon} expiring` : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {certs.map(c => (
          <div key={c.domain} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{c.domain}</span>
            <span className={c.expiresDays <= 30 ? "text-yellow-600" : "text-gray-400"}>
              {c.expiresDays}d left
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
