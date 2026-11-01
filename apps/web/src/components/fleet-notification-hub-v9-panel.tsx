"use client";
export function FleetNotificationHubV9Panel({ channels, sent }: { channels: number; sent: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 Notification Hub v9</h3>
    <div className="text-sm">{channels} channels · {sent.toLocaleString()} sent</div>
  </div>);
}
