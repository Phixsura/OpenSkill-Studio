"use client";
export function FleetAiNotifHubPanel({ hubs, active, channels, sent, deliveryRate }: { hubs: number; active: number; channels: number; sent: number; deliveryRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 AI Notification Hub</h3>
    <div className="text-sm">{active}/{hubs} active · {channels} channels · {sent.toLocaleString()} sent · {deliveryRate}% delivered</div>
  </div>);
}
