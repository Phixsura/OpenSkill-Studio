"use client";

interface SubscriptionInfo {
  subscription_id: string;
  event_types: string[] | null;
  active: boolean;
  delivery_count: number;
}

interface RecentEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
}

interface EventBusCardProps {
  subscriptions: SubscriptionInfo[];
  recentEvents: RecentEvent[];
  appName: string;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function EventBusCard({ subscriptions, recentEvents, appName }: EventBusCardProps) {
  const activeCount = subscriptions.filter((s) => s.active).length;
  const totalDelivered = subscriptions.reduce((s, sub) => s + sub.delivery_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Event Bus</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{activeCount} subscribers</span>
          <span className="text-xs text-gray-400">· {totalDelivered} delivered</span>
        </div>
      </div>

      {/* Subscriptions */}
      {subscriptions.length > 0 && (
        <div className="mb-3">
          <p className="mb-1.5 text-xs font-medium text-gray-500">Subscriptions</p>
          <div className="space-y-1.5">
            {subscriptions.map((sub) => (
              <div
                key={sub.subscription_id}
                className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${sub.active ? "bg-green-500" : "bg-gray-300"}`}
                  />
                  <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
                    {sub.subscription_id}
                  </span>
                  {sub.event_types ? (
                    <span className="text-[10px] text-gray-400">
                      {sub.event_types.length} types
                    </span>
                  ) : (
                    <span className="text-[10px] text-purple-500">wildcard</span>
                  )}
                </div>
                <span className="text-[11px] text-gray-400">{sub.delivery_count} events</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Events */}
      {recentEvents.length > 0 && (
        <div className="border-t border-gray-100 pt-3 dark:border-gray-800">
          <p className="mb-1.5 text-xs font-medium text-gray-500">Recent Events</p>
          <div className="space-y-1">
            {recentEvents.map((evt) => (
              <div key={evt.event_id} className="flex items-center justify-between text-xs">
                <span className="font-mono text-gray-700 dark:text-gray-300">{evt.event_type}</span>
                <span className="text-[11px] text-gray-400">{timeAgo(evt.timestamp)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {subscriptions.length === 0 && recentEvents.length === 0 && (
        <p className="text-center text-sm text-gray-400">No event activity</p>
      )}
    </div>
  );
}
