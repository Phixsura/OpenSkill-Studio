"use client";
export function FleetAiSvcCatPanel({ catalogs, active, services, owners, documented }: { catalogs: number; active: number; services: number; owners: number; documented: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Service Catalog</h3>
    <div className="text-sm">{active}/{catalogs} active · {services} services · {owners} owners · {documented}% documented</div>
  </div>);
}
