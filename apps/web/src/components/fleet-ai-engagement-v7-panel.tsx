"use client";
export function FleetAiEngagementV7Panel({ trackers, active, dauMau, sessions, time }: { trackers: number; active: number; dauMau: number; sessions: number; time: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Engagement v7</h3>
    <div className="text-sm">{active}/{trackers} active · DAU/MAU {dauMau}% · {sessions} sessions · {time}m/session</div>
  </div>);
}
