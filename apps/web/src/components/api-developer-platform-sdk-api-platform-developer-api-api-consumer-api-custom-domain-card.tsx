"use client";

interface DomainInfo { domain_id: string; domain: string; status: string; ssl_enabled: boolean; consumer_id: string; }
interface Props { domains: DomainInfo[]; appName: string; }

const statusColor: Record<string, string> = { pending: "text-yellow-600 dark:text-yellow-400", verified: "text-blue-600 dark:text-blue-400", active: "text-green-600 dark:text-green-400", failed: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCustomDomainCard({ domains, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 Custom Domains</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {domains.length} domains</p>
      </div>
      {domains.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom domains</p>
      ) : (
        <div className="space-y-1">
          {domains.map((d) => (
            <div key={d.domain_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                {d.ssl_enabled && <span className="text-green-500">🔒</span>}
                <span className="font-mono text-gray-700 dark:text-gray-300">{d.domain}</span>
              </div>
              <span className={statusColor[d.status] ?? "text-gray-400"}>{d.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
