"use client";
export function FleetGrafbasePanel({ projects, deployed, resolvers, requests }: { projects: number; deployed: number; resolvers: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">◆ Grafbase</h3>
    <div className="text-sm">{deployed}/{projects} deployed · {resolvers} resolvers · {requests.toLocaleString()} req</div>
  </div>);
}
