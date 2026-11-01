"use client";

interface SsoInfo { config_id: string; consumer_id: string; provider: string; enabled: boolean; enforce: boolean; domains: string[]; }
interface Props { configs: SsoInfo[]; appName: string; }

const providerIcon: Record<string, string> = { saml: "🔑", oidc: "🪪", oauth2: "🔐" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSsoConfigCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 SSO Config</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} consumers</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SSO configured</p>
      ) : (
        <div className="space-y-1.5">
          {configs.map((c) => (
            <div key={c.config_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span>{providerIcon[c.provider] ?? "•"}</span>
                  <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className={c.enabled ? "text-green-600 dark:text-green-400" : "text-gray-400"}>{c.enabled ? "on" : "off"}</span>
                  {c.enforce && <span className="rounded bg-red-100 px-1 text-[9px] text-red-700 dark:bg-red-900/30 dark:text-red-400">enforced</span>}
                </div>
              </div>
              {c.domains.length > 0 && <div className="text-[10px] text-gray-400">{c.domains.join(", ")}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
