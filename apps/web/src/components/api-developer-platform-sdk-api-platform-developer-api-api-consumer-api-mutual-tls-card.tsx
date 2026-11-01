"use client";

interface CertInfo { cert_id: string; consumer_id: string; subject_cn: string; status: string; fingerprint_short: string; }
interface Props { certs: CertInfo[]; activeCertCount: number; appName: string; }

const statusIcon: Record<string, string> = { active: "🟢", expired: "🟡", revoked: "🔴" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMutualTlsCard({ certs, activeCertCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Mutual TLS</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCertCount} active</p>
        </div>
      </div>
      {certs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No mTLS certificates</p>
      ) : (
        <div className="space-y-1">
          {certs.map((c) => (
            <div key={c.cert_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{statusIcon[c.status] ?? "⚪"}</span>
                <span className="text-gray-700 dark:text-gray-300">{c.subject_cn}</span>
              </div>
              <span className="font-mono text-[9px] text-gray-400">{c.fingerprint_short}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
