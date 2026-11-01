"use client";
export function FleetAiDnsPanel({ resolvers, active, queries, cacheHit, services }: { resolvers: number; active: number; queries: number; cacheHit: number; services: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI DNS Resolver</h3>
    <div className="text-sm">{active}/{resolvers} active · {queries.toLocaleString()} queries · {cacheHit}% cache · {services} services</div>
  </div>);
}
