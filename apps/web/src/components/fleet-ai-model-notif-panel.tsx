"use client";
export function FleetAiModelNotifPanel({ systems, active, notifications, channels, subscribers }: { systems: number; active: number; notifications: number; channels: number; subscribers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 AI Model Notifications</h3>
    <div className="text-sm">{active}/{systems} active · {notifications.toLocaleString()} notifs · {channels} channels · {subscribers.toLocaleString()} subs</div>
  </div>);
}
