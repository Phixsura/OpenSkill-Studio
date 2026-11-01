"use client";
export function FleetAiModelHostPanel({ hosts, active, models, endpoints, uptime }: { hosts: number; active: number; models: number; endpoints: number; uptime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏠 AI Model Hosting</h3>
    <div className="text-sm">{active}/{hosts} active · {models} models · {endpoints} endpoints · {uptime}% uptime</div>
  </div>);
}
