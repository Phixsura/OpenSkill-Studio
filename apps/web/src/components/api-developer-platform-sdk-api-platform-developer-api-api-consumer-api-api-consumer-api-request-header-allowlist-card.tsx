"use client";

interface AllowlistInfo { consumer_id: string; allowed_count: number; strip_unknown: boolean; }
interface Props { allowlists: AllowlistInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestHeaderAllowlistCard({ allowlists, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Header Allowlist</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {allowlists.length} consumers</p>
      </div>
      {allowlists.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No header allowlists</p>
      ) : (
        <div className="space-y-1">
          {allowlists.map((a) => (
            <div key={a.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{a.consumer_id}</span>
              <span className="text-gray-400">{a.allowed_count} allowed{a.strip_unknown ? " · strip" : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
