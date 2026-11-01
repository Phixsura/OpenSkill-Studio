"use client";
export function FleetPosthogPanel({ instances, running, events, featureFlags }: { instances: number; running: number; events: number; featureFlags: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦔 PostHog</h3>
    <div className="text-sm">{running}/{instances} running · {events.toLocaleString()} events · {featureFlags} flags</div>
  </div>);
}
