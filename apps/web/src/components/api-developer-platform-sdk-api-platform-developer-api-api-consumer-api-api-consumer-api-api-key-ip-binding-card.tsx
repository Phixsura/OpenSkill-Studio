"use client";

interface BindingInfo { key_id: string; consumer_id: string; allowed_ips: string[]; enforce: boolean; violations: number; }
interface Props { bindings: BindingInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyIpBindingCard({ bindings, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 Key IP Binding</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {bindings.length} bindings</p>
      </div>
      {bindings.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No IP bindings</p>
      ) : (
        <div className="space-y-1.5">
          {bindings.map((b) => (
            <div key={b.key_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="font-mono text-gray-700 dark:text-gray-300">{b.key_id}</span>
                <span className="text-gray-400">{b.violations > 0 ? `🚫 ${b.violations}` : "✅"}{b.enforce ? "" : " (monitor)"}</span>
              </div>
              <div className="flex gap-1 mt-0.5">{b.allowed_ips.map((ip) => <span key={ip} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{ip}</span>)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
