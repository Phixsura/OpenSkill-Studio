"use client";
export function FleetDenoPanel({ projects, deployed, requests, avgIsolate }: { projects: number; deployed: number; requests: number; avgIsolate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦕 Deno Deploy</h3>
    <div className="text-sm">{deployed}/{projects} deployed · {requests.toLocaleString()} req/24h · {avgIsolate}ms</div>
  </div>);
}
