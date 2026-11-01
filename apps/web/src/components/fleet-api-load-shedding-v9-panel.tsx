"use client";
export function FleetApiLoadSheddingV9Panel({ services, shedding }: { services: number; shedding: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ Load Shedding v9</h3>
    <div className="text-sm">{services} services · {shedding} shedding</div>
  </div>);
}
