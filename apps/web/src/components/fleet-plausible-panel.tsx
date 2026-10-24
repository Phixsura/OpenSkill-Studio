"use client";
export function FleetPlausiblePanel({ sites, active, pageviews, visitors }: { sites: number; active: number; pageviews: number; visitors: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Plausible</h3>
    <div className="text-sm">{active}/{sites} active · {pageviews.toLocaleString()} views · {visitors.toLocaleString()} visitors</div>
  </div>);
}
