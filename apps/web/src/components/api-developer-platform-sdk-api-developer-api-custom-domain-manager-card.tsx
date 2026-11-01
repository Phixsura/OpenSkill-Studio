"use client";

interface DomainInfo { domain: string; status: string; ssl_status: string; }
interface Props { domains: DomainInfo[]; appName: string; }

const sColor: Record<string, string> = { pending: "bg-yellow-100 text-yellow-700", verified: "bg-blue-100 text-blue-700", active: "bg-green-100 text-green-700", failed: "bg-red-100 text-red-700" };

export default function APIDeveloperPlatformSDKApiDeveloperApiCustomDomainManagerCard({ domains, appName }: Props) {
  const activeCount = domains.filter(d => d.status === "active").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 Custom Domains</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount}/{domains.length} active</p>
      </div>
      {domains.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom domains</p>
      ) : (
        <div className="space-y-1.5">
          {domains.map((d) => (
            <div key={d.domain} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{d.domain}</span>
              <div className="flex gap-1">
                <span className={`rounded px-1 py-0.5 text-[9px] ${sColor[d.status] ?? ""}`}>{d.status}</span>
                {d.ssl_status === "provisioned" && <span className="text-[9px] text-green-600">🔒</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
