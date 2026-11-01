"use client";
export function FleetAiWtTrackPanel({ trackers, active, models, checkpoints, drift }: { trackers: number; active: number; models: number; checkpoints: number; drift: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Weight Tracker</h3>
    <div className="text-sm">{active}/{trackers} active · {models} models · {checkpoints.toLocaleString()} ckpts · {drift} drift events</div>
  </div>);
}
