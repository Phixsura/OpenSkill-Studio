"use client";
export function FleetAiPlatEvhubV2Panel({ hubs, active, events, topics, consumers }: { hubs: number; active: number; events: number; topics: number; consumers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Event Hub v2</h3>
    <div className="text-sm">{active}/{hubs} active · {events.toLocaleString()} events · {topics} topics · {consumers.toLocaleString()} consumers</div>
  </div>);
}
