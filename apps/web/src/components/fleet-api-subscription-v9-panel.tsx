"use client";
export function FleetApiSubscriptionV9Panel({ subs, events }: { subs: number; events: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 API Subscription v9</h3>
    <div className="text-sm">{subs} subscriptions · {events.toLocaleString()} events</div>
  </div>);
}
