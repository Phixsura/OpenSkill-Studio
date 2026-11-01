"use client";
export function FleetAiPlatNotifV3Panel({ systems, active, sent, channels, delivery }: { systems: number; active: number; sent: number; channels: number; delivery: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 AI Notification v3</h3>
    <div className="text-sm">{active}/{systems} active · {sent.toLocaleString()} sent · {channels} channels · {delivery}% delivered</div>
  </div>);
}
