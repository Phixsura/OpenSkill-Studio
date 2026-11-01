"use client";

interface EventTypeInfo { eventType: string; subscribers: number; }
interface EventBusPanelProps { eventTypes: EventTypeInfo[]; published: number; delivered: number; }

export function EventBusPanel({ eventTypes, published, delivered }: EventBusPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 Event Bus</h3>
        <span className="text-xs text-gray-400">{published.toLocaleString()} pub · {delivered.toLocaleString()} delivered</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {eventTypes.map(e => (
          <div key={e.eventType} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.eventType}</span>
            <span className="text-gray-400">{e.subscribers} subs</span>
          </div>
        ))}
      </div>
    </div>
  );
}
