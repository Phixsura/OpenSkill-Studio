"use client";
export function FleetAiIncTimelinePanel({ trackers, active, incidents, events, resolution }: { trackers: number; active: number; incidents: number; events: number; resolution: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ AI Incident Timeline</h3>
    <div className="text-sm">{active}/{trackers} active · {incidents} incidents · {events.toLocaleString()} events · {resolution}m MTTR</div>
  </div>);
}
