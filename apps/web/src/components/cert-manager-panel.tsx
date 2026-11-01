"use client";

interface CertStatus { domain: string; daysLeft: number; status: string; needsRenewal: boolean; }
interface CertManagerPanelProps { certs: CertStatus[]; needsAction: boolean;
  onRenew: (domain: string) => void; }

const STATUS_STYLE: Record<string, { color: string; icon: string }> = {
  valid: { color: "text-green-600", icon: "🟢" },
  expiring_soon: { color: "text-yellow-600", icon: "🟡" },
  expired: { color: "text-red-600", icon: "🔴" },
};

export function CertManagerPanel({ certs, needsAction, onRenew }: CertManagerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 TLS Certificates</h3>
        {needsAction && <span className="text-xs text-red-500">⚠ Action Required</span>}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {certs.map(c => {
          const s = STATUS_STYLE[c.status] ?? STATUS_STYLE.valid;
          return (
            <div key={c.domain} className="flex items-center justify-between px-4 py-2.5">
              <div className="flex items-center gap-2">
                <span>{s.icon}</span>
                <span className="text-sm font-mono">{c.domain}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs ${s.color}`}>{c.daysLeft}d left</span>
                {c.needsRenewal && (
                  <button onClick={() => onRenew(c.domain)}
                    className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">Renew</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
