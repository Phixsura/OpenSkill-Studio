"use client";

interface EventEntry { topic: string; deliveredTo: number; }
interface EventBusDashboardProps { topics: Record<string, string[]>; topicCount: number;
  totalSubscriptions: number; recentEvents: EventEntry[]; }

export function EventBusDashboard({ topics, topicCount, totalSubscriptions, recentEvents }: EventBusDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 Event Bus</h3>
        <span className="text-xs text-gray-400">{topicCount} topics · {totalSubscriptions} subs</span>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700">
        <div className="p-3">
          <div className="text-xs text-gray-400 mb-2">Topics & Handlers</div>
          {Object.entries(topics).map(([topic, handlers]) => (
            <div key={topic} className="mb-2">
              <div className="text-xs font-mono font-medium">{topic}</div>
              {handlers.map(h => (
                <div key={h} className="text-[10px] text-gray-400 pl-2">→ {h}</div>
              ))}
            </div>
          ))}
        </div>
        <div className="p-3">
          <div className="text-xs text-gray-400 mb-2">Recent Events</div>
          {recentEvents.map((e, i) => (
            <div key={i} className="flex justify-between text-xs py-0.5">
              <span className="font-mono">{e.topic}</span>
              <span className="text-gray-400">→ {e.deliveredTo}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
