"use client";
export function FleetAppsyncPanel({ apis, active, requests, errors4xx, errors5xx }: { apis: number; active: number; requests: number; errors4xx: number; errors5xx: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">◆ AppSync</h3>
    <div className="text-sm">{active}/{apis} active · {requests.toLocaleString()} req · {errors5xx} 5xx</div>
  </div>);
}
