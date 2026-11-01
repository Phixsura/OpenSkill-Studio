"use client";
export function FleetApigwAwsPanel({ apis, deployed, requests, throttled }: { apis: number; deployed: number; requests: number; throttled: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 API Gateway</h3>
    <div className="text-sm">{deployed}/{apis} deployed · {requests.toLocaleString()} req · {throttled} throttled</div>
  </div>);
}
