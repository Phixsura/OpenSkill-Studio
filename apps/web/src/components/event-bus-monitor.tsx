"use client";

interface BusEvent { eventId: string; topic: string; publisherId: string; timestamp: number; }
interface TopicInfo { topic: string; subscriberCount: number; eventCount: number; }

export function EventBusMonitor({ topics, recentEvents }: { topics: TopicInfo[]; recentEvents: BusEvent[] }) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="font-bold text-sm mb-2">Topics ({topics.length})</h3>
        <div className="flex flex-wrap gap-1">
          {topics.map(t => (
            <span key={t.topic} className="text-xs border dark:border-gray-700 rounded-full px-2.5 py-1">
              {t.topic} <span className="text-gray-400">({t.subscriberCount} subs · {t.eventCount} events)</span>
            </span>
          ))}
        </div>
      </div>
      <div>
        <h3 className="font-bold text-sm mb-2">Recent Events</h3>
        {recentEvents.length === 0 ? (
          <div className="text-center text-gray-400 py-4 text-sm">No events yet</div>
        ) : (
          <div className="space-y-1">
            {recentEvents.map(e => (
              <div key={e.eventId} className="flex items-center justify-between text-xs border dark:border-gray-700 rounded-lg p-2">
                <div className="flex items-center gap-2">
                  <span className="bg-blue-100 dark:bg-blue-900/20 text-blue-600 px-1.5 py-0.5 rounded">{e.topic}</span>
                  <span className="text-gray-500">from {e.publisherId}</span>
                </div>
                <span className="text-gray-400">{e.eventId}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
