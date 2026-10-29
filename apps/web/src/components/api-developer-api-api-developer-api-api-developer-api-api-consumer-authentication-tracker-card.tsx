"use client";

interface RecordInfo { consumer_id: string; auth_method: string; successful: number; failed: number; failure_rate: number; }
interface Props { records: RecordInfo[]; methodCounts: Record<string, number>; highFailureCount: number; appName: string; }

const mBadge: Record<string, string> = { api_key: "bg-blue-100 text-blue-700", oauth2: "bg-green-100 text-green-700", jwt: "bg-purple-100 text-purple-700", basic: "bg-gray-100 text-gray-600" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTrackerCard({ records, methodCounts, highFailureCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Auth Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {highFailureCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{highFailureCount} high failure</span>}
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(methodCounts).map(([m, c]) => (
          <span key={m} className={`rounded px-1.5 py-0.5 text-[10px] ${mBadge[m] ?? ""}`}>{m}: {c}</span>
        ))}
      </div>
      {records.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No auth data</p>
      ) : (
        <div className="space-y-1">
          {records.slice(0, 5).map((r) => (
            <div key={r.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{r.consumer_id}</span>
              <span className={r.failure_rate > 10 ? "text-red-500" : "text-gray-400"}>{r.failure_rate}% fail · {r.successful + r.failed} total</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
