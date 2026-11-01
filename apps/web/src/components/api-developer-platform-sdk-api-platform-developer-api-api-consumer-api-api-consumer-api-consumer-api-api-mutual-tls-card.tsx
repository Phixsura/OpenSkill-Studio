"use client";

interface Cert { id: string; cn: string; fingerprint: string; issuer: string; expiresAt: string; revoked: boolean; }
interface Props { certs: Cert[]; consumerId: string; mtlsRequired: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiMutualTlsCard({ certs, consumerId, mtlsRequired, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Mutual TLS</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${mtlsRequired ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-gray-200 text-gray-500"}`}>{mtlsRequired ? "Required" : "Optional"}</span>
      </div>
      {certs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No certificates</p>
      ) : (
        <div className="space-y-2">
          {certs.map((c) => (
            <div key={c.id} className={`rounded-lg bg-gray-50 p-2 dark:bg-gray-800 ${c.revoked ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{c.cn}</span>
                {c.revoked && <span className="text-[10px] text-red-500">Revoked</span>}
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">
                <code>{c.fingerprint.slice(0, 16)}...</code> · {c.issuer} · Exp: {c.expiresAt}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
