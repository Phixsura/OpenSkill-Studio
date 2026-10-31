"use client";

interface CertInfo { domain: string; issuer: string; daysUntilExpiry: number;
  status: string; autoRenew: boolean; }
interface SslCertStatusProps { certs: CertInfo[]; overall: string;
  valid: number; expiringSoon: number; expired: number; }

const STATUS_BADGE: Record<string, string> = {
  valid: "bg-green-100 text-green-700", expiring: "bg-yellow-100 text-yellow-700",
  expired: "bg-red-100 text-red-700",
};

export function SslCertStatus({ certs, overall, valid, expiringSoon, expired }: SslCertStatusProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔒 SSL Certificates</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          overall === "healthy" ? "bg-green-100 text-green-700" :
          overall === "warning" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
        }`}>{overall}</span>
      </div>
      <div className="flex gap-4 text-xs mb-4">
        <span className="text-green-600">{valid} valid</span>
        {expiringSoon > 0 && <span className="text-yellow-600">{expiringSoon} expiring</span>}
        {expired > 0 && <span className="text-red-600">{expired} expired</span>}
      </div>
      <div className="space-y-2">
        {certs.map(c => (
          <div key={c.domain} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <div>
              <span className="text-sm font-mono">{c.domain}</span>
              <span className="text-xs text-gray-400 ml-2">{c.issuer}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{c.daysUntilExpiry}d</span>
              {c.autoRenew && <span className="text-xs text-green-500">🔄</span>}
              <span className={`text-xs px-1.5 py-0.5 rounded ${STATUS_BADGE[c.status] || ""}`}>{c.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
