"use client";
export function FleetAiRetentionV7Panel({ trackers, active, d1, d7, d30, d90 }: { trackers: number; active: number; d1: number; d7: number; d30: number; d90: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Retention v7</h3>
    <div className="text-sm">{active}/{trackers} active · D1 {d1}% · D7 {d7}% · D30 {d30}% · D90 {d90}%</div>
  </div>);
}
