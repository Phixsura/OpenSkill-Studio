"use client";

interface Event { id: string; actor: string; action: string; resourceType: string; resourceId: string; description: string; timestamp: string; }
interface Props { events: Event[]; consumerId: string; appName: string; }

const actionIcons: Record<string, string> = { created: "➕", updated: "✏️", deleted: "🗑️", rotated: "🔄", revoked: "❌" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerActivityFeedCard({ events, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Activity Feed</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No recent activity</p>
      ) : (
        <div className="space-y-1">
          {events.slice(0, 8).map((e) => (
            <div key={e.id} className="flex items-start gap-1.5 text-[10px]">
              <span>{actionIcons[e.action] ?? "📌"}</span>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">{e.actor}</span>
                <span className="text-gray-400"> {e.action} </span>
                <span className="text-gray-500">{e.resourceType}/{e.resourceId}</span>
                <span className="ml-1 text-[9px] text-gray-400">{e.timestamp}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
