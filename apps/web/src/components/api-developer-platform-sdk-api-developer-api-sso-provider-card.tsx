"use client";

interface ProviderInfo { provider_id: string; provider_type: string; issuer_url: string; enabled: boolean; login_count: number; }
interface Props { providers: ProviderInfo[]; appName: string; }

const tBadge: Record<string, string> = { saml: "bg-purple-100 text-purple-700", oidc: "bg-blue-100 text-blue-700", oauth2: "bg-green-100 text-green-700" };

export default function APIDeveloperPlatformSDKApiDeveloperApiSSOProviderCard({ providers, appName }: Props) {
  const activeCount = providers.filter(p => p.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 SSO Providers</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount}/{providers.length} active</p>
      </div>
      {providers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SSO providers</p>
      ) : (
        <div className="space-y-2">
          {providers.map((p) => (
            <div key={p.provider_id} className={`rounded-lg px-3 py-2 ${p.enabled ? "bg-gray-50 dark:bg-gray-800" : "bg-gray-100 opacity-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] ${tBadge[p.provider_type] ?? ""}`}>{p.provider_type}</span>
                  <span className="text-gray-700 dark:text-gray-300">{p.provider_id}</span>
                </div>
                <span className="text-gray-400">{p.login_count} logins</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
