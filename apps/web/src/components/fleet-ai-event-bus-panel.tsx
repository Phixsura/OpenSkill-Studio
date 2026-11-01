"use client";
export function FleetAiEventBusPanel({ buses, active, events, subscribers, topics }: { buses: number; active: number; events: number; subscribers: number; topics: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Event Bus</h3>
    <div className="text-sm">{active}/{buses} active · {events.toLocaleString()} events · {subscribers} subs · {topics} topics</div>
  </div>);
}
