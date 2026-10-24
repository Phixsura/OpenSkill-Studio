"use client";

interface TopicInfo { topic: string; subscribers: number; }
interface EventBusMonitorProps { topics: TopicInfo[]; totalSubscribers: number;
  published: number; delivered: number; }

export function EventBusMonitor({ topics, totalSubscribers, published, delivered }: EventBusMonitorProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">📬 Event Bus</h3>
      <div className="grid grid-cols-4 gap-3 text-center mb-4">
        <div><p className="text-lg font-bold">{topics.length}</p><p className="text-xs text-gray-400">Topics</p></div>
        <div><p className="text-lg font-bold">{totalSubscribers}</p><p className="text-xs text-gray-400">Subscribers</p></div>
        <div><p className="text-lg font-bold">{published.toLocaleString()}</p><p className="text-xs text-gray-400">Published</p></div>
        <div><p className="text-lg font-bold">{delivered.toLocaleString()}</p><p className="text-xs text-gray-400">Delivered</p></div>
      </div>
      <div className="space-y-1">
        {topics.map(t => (
          <div key={t.topic} className="flex justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5">
            <span className="font-mono text-xs">{t.topic}</span>
            <span className="text-xs text-gray-400">{t.subscribers} subs</span>
          </div>
        ))}
      </div>
    </div>
  );
}
