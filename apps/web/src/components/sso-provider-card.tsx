"use client";

interface SSOProviderInfo {
  provider_id: string;
  provider_type: string;
  name: string;
  issuer_url: string;
  enabled: boolean;
  success_rate: number;
  auth_count: number;
}

interface SSOProviderCardProps {
  providers: SSOProviderInfo[];
  appName: string;
}

export default function SSOProviderCard({ providers, appName }: SSOProviderCardProps) {
  const enabled = providers.filter((p) => p.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔑 SSO Providers
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {enabled}/{providers.length} enabled
        </span>
      </div>

      {providers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SSO providers</p>
      ) : (
        <div className="space-y-2">
          {providers.map((p) => (
            <div
              key={p.provider_id}
              className={`rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!p.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                    {p.name}
                  </span>
                  <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                    {p.provider_type.toUpperCase()}
                  </span>
                </div>
                <span className="text-[11px] text-gray-400">
                  {p.success_rate}% · {p.auth_count} auths
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
