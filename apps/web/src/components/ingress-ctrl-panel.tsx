"use client";

interface IngressRule { host: string; path: string; backend: string; tls: boolean; }
interface CertInfo { domain: string; expiresDays: number; issuer: string; }
interface IngressCtrlPanelProps { rules: IngressRule[]; certs: CertInfo[]; tlsEnabled: number; }

export function IngressCtrlPanel({ rules, certs, tlsEnabled }: IngressCtrlPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚪 Ingress Controller</h3>
        <span className="text-xs text-gray-400">{rules.length} rules · {tlsEnabled} TLS · {certs.length} certs</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rules.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.host}{r.path}</span>
            <div className="flex items-center gap-2">
              <span className="text-blue-500">{r.backend}</span>
              {r.tls && <span className="text-green-600">🔒</span>}
            </div>
          </div>
        ))}
      </div>
      {certs.some(c => c.expiresDays <= 30) && (
        <div className="border-t dark:border-gray-700 p-3 text-xs text-yellow-600">
          ⚠ {certs.filter(c => c.expiresDays <= 30).length} cert(s) expiring soon
        </div>
      )}
    </div>
  );
}
