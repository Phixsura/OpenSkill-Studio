"use client";

interface Topic { name: string; subscribers: number; events_24h: number; avg_latency_ms: number; }
interface EventBusTopicsProps { topics: Topic[]; totalEvents24h: number; onSubscribe: (topic: string) => void; }

export function EventBusTopics({ topics, totalEvents24h, onSubscribe }: EventBusTopicsProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Event Bus</h2>
        <span className="text-xs text-gray-400">{totalEvents24h.toLocaleString()} events/24h</span>
      </div>
      <div className="space-y-1.5">
        {topics.map(t => (
          <div key={t.name} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div>
              <p className="font-mono text-sm font-medium">{t.name}</p>
              <p className="text-xs text-gray-400">{t.subscribers} subscribers · {t.events_24h} events · {t.avg_latency_ms}ms avg</p>
            </div>
            <button onClick={() => onSubscribe(t.name)} className="rounded bg-blue-600 px-2 py-1 text-xs text-white">
              Subscribe
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
