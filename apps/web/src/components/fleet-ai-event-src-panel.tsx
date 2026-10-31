"use client";
export function FleetAiEventSrcPanel({ stores, active, events, streams, projections }: { stores: number; active: number; events: number; streams: number; projections: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Event Sourcing</h3>
    <div className="text-sm">{active}/{stores} active · {events.toLocaleString()} events · {streams.toLocaleString()} streams · {projections} projections</div>
  </div>);
}
