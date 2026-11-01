"use client";
export function FleetCloudrunPanel({ services, active, revisions, requests, avgLatency }: { services: number; active: number; revisions: number; requests: number; avgLatency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Cloud Run</h3>
    <div className="text-sm">{active}/{services} active · {revisions} revisions · {requests.toLocaleString()} req · {avgLatency}ms</div>
  </div>);
}
