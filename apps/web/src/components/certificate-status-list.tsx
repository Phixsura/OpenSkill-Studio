"use client";

interface CertStatus { domain: string; days_until_expiry: number; status: string; auto_renew: boolean; }
interface CertificateStatusListProps { certificates: CertStatus[]; onRenew: (domain: string) => void; }

const statusStyle: Record<string, string> = {
  valid: "bg-green-100 text-green-700 dark:bg-green-900/30",
  expiring: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  expired: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function CertificateStatusList({ certificates, onRenew }: CertificateStatusListProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">SSL Certificates</h2>
      {certificates.map(c => (
        <div key={c.domain} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
          <div>
            <p className="font-mono text-sm font-medium">{c.domain}</p>
            <p className="text-xs text-gray-400">
              {c.days_until_expiry > 0 ? `${c.days_until_expiry} days left` : "Expired"}
              {c.auto_renew && " · Auto-renew"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`rounded-full px-2 py-0.5 text-xs ${statusStyle[c.status] ?? ""}`}>{c.status}</span>
            {c.status !== "valid" && (
              <button onClick={() => onRenew(c.domain)} className="rounded bg-blue-600 px-2 py-1 text-xs text-white">Renew</button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
