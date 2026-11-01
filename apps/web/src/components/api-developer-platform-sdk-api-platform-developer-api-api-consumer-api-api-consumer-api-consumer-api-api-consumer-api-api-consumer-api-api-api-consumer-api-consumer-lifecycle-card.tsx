"use client";

interface Account { id: string; name: string; status: string; plan: string; createdAt: string; }
interface Props { accounts: Account[]; statusCounts: Record<string, number>; appName: string; }

const statusColors: Record<string, string> = {
  pending: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
  active: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  suspended: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  deactivated: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerLifecycleCard({ accounts, statusCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Consumer Lifecycle</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(statusCounts).map(([s, c]) => (
          <span key={s} className={`rounded px-1.5 py-0.5 text-[9px] ${statusColors[s] ?? "bg-gray-200 text-gray-600"}`}>{s}: {c}</span>
        ))}
      </div>
      {accounts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No consumers</p>
      ) : (
        <div className="space-y-1">
          {accounts.slice(0, 8).map((a) => (
            <div key={a.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
              <span className="text-gray-700 dark:text-gray-300">{a.name}</span>
              <div className="flex gap-1">
                <span className="text-[10px] text-gray-400">{a.plan}</span>
                <span className={`rounded px-1 py-0.5 text-[9px] ${statusColors[a.status] ?? ""}`}>{a.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
