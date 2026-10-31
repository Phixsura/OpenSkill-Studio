"use client";
export function FleetSegmentPanel({ workspaces, active, events, sources, destinations }: { workspaces: number; active: number; events: number; sources: number; destinations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Segment</h3>
    <div className="text-sm">{active}/{workspaces} active · {events.toLocaleString()} events · {sources}→{destinations}</div>
  </div>);
}
