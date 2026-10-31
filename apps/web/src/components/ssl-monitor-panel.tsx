"use client";

interface CertInfo { domain: string; issuer: string; daysUntilExpiry: number; }
interface SslMonitorPanelProps { valid: number; expiringSoon: number; expired: number;
  critical: boolean; certs: CertInfo[]; }

export function SslMonitorPanel({ valid, expiringSoon, expired, critical, certs }: SslMonitorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 SSL Certificates</h3>
        <span className={`text-xs font-bold ${critical ? "text-red-500" : expiringSoon > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {critical ? `❌ ${expired} expired` : expiringSoon > 0 ? `⚠ ${expiringSoon} expiring` : `✅ ${valid} valid`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {certs.map(c => (
          <div key={c.domain} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{c.domain}</span>
            <span className={c.daysUntilExpiry <= 0 ? "text-red-600 font-bold" : c.daysUntilExpiry <= 30 ? "text-yellow-600" : "text-gray-400"}>
              {c.daysUntilExpiry <= 0 ? "EXPIRED" : `${c.daysUntilExpiry}d left`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
