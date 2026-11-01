"use client";
export function FleetEventbridgePanel({ buses, events, rules, failedInvocations }: { buses: number; events: number; rules: number; failedInvocations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 EventBridge</h3>
    <div className="text-sm">{buses} buses · {events.toLocaleString()} events · {rules} rules</div>
  </div>);
}
