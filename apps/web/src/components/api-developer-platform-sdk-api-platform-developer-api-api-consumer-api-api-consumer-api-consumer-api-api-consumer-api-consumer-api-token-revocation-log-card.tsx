"use client";

interface Event { id: string; tokenId: string; reason: string; revokedBy: string; timestamp: string; }
interface Props { events: Event[]; byReason: Record<string, number>; totalRevocations: number; consumerId: string; appName: string; }

const reasonColors: Record<string, string> = {
  manual: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  rotation: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  compromise: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  expiry: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
  policy: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  abuse: "bg-red-200 text-red-800 dark:bg-red-900/40 dark:text-red-300",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiTokenRevocationLogCard({ events, byReason, totalRevocations, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 Revocation Log</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {totalRevocations} revocations</p>
      </div>
      {Object.keys(byReason).length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1">
          {Object.entries(byReason).map(([r, c]) => (
            <span key={r} className={`rounded px-1.5 py-0.5 text-[9px] ${reasonColors[r] ?? "bg-gray-200 text-gray-600"}`}>{r}: {c}</span>
          ))}
        </div>
      )}
      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No revocations</p>
      ) : (
        <div className="space-y-0.5">
          {events.slice(0, 6).map((e) => (
            <div key={e.id} className="flex items-center justify-between text-[10px]">
              <div className="flex items-center gap-1">
                <span className={`rounded px-1 py-0.5 text-[9px] ${reasonColors[e.reason] ?? ""}`}>{e.reason}</span>
                <code className="text-gray-500">{e.tokenId}</code>
              </div>
              <span className="text-gray-400">{e.revokedBy} · {e.timestamp}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
