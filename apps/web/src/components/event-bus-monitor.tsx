"use client";

interface EventEntry { event: string; subscriberCount: number; timestamp: string; }
interface Subscription { handlerId: string; name: string; event: string; }
interface EventBusMonitorProps { events: EventEntry[]; subscriptions: Subscription[]; eventTypes: string[]; }

export function EventBusMonitor({ events, subscriptions, eventTypes }: EventBusMonitorProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Event Bus</h3>
        <span className="text-xs text-gray-400">{eventTypes.length} event types · {subscriptions.length} subscribers</span>
      </div>
      <div className="max-h-48 overflow-y-auto divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {events.map((e, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2">
              <span className="text-xs">📡</span>
              <span className="text-sm font-mono">{e.event}</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span>{e.subscriberCount} subs</span>
              <time>{new Date(e.timestamp).toLocaleTimeString()}</time>
            </div>
          </div>
        ))}
        {events.length === 0 && <p className="py-4 text-center text-sm text-gray-400">No events yet</p>}
      </div>
    </div>
  );
}
