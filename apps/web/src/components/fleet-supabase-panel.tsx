"use client";
export function FleetSupabasePanel({ projects, active, dbSize, apiRequests }: { projects: number; active: number; dbSize: number; apiRequests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Supabase</h3>
    <div className="text-sm">{active}/{projects} active · {dbSize}GB · {apiRequests.toLocaleString()} req/24h</div>
  </div>);
}
