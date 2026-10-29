"use client";

interface AllowlistInfo { allowlist_id: string; entries: string[]; allowed_count: number; blocked_count: number; }
interface Props { allowlists: AllowlistInfo[]; appName: string; }

export default function APIDeveloperAPIWebhookIPAllowlistCard({ allowlists, appName }: Props) {
  const totalBlocked = allowlists.reduce((s, a) => s + a.blocked_count, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 IP Allowlist</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {totalBlocked > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{totalBlocked} blocked</span>}
      </div>
      {allowlists.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No allowlists</p>
      ) : (
        <div className="space-y-2">
          {allowlists.map((a) => (
            <div key={a.allowlist_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{a.allowlist_id}</span>
                <span className="text-gray-400">{a.entries.length} entries</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px]">
                <span className="text-green-600">{a.allowed_count} allowed</span>
                <span className="text-red-500">{a.blocked_count} blocked</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
