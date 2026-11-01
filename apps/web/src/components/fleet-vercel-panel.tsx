"use client";
export function FleetVercelPanel({ projects, deployed, requests, edgeFunctions }: { projects: number; deployed: number; requests: number; edgeFunctions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">▲ Vercel</h3>
    <div className="text-sm">{deployed}/{projects} deployed · {requests.toLocaleString()} req/24h · {edgeFunctions} edge fn</div>
  </div>);
}
