"use client";
export function FleetMktAnalyticsPanel({ listings, installs, avgRating, installRate }: { listings: number; installs: number; avgRating: number; installRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏪 Marketplace</h3>
    <div className="text-sm">{listings} listings · {installs.toLocaleString()} installs · ⭐ {avgRating}</div>
    <div className="text-xs text-gray-400">{installRate} installs/listing avg</div>
  </div>);
}
