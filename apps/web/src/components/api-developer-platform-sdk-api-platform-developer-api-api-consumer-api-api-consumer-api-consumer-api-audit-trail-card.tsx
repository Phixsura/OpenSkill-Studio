"use client";

interface Event { id: string; action: string; actorId: string; resourceType: string; resourceId: string; timestamp: string; }
interface Props { events: Event[]; consumerId: string; totalCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiAuditTrailCard({ events, consumerId, totalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Audit Trail</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {totalCount} total events</p>
      </div>
      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No audit events</p>
      ) : (
        <div className="space-y-1">
          {events.slice(0, 10).map((e) => (
            <div key={e.id} className="rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-700 dark:text-gray-300">{e.action}</span>
                <span className="text-gray-400">{e.timestamp}</span>
              </div>
              <div className="text-gray-400">by {e.actorId} · {e.resourceType}/{e.resourceId}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
