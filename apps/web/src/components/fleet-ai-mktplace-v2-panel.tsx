"use client";
export function FleetAiMktplaceV2Panel({ marketplaces, active, listings, publishers, installs }: { marketplaces: number; active: number; listings: number; publishers: number; installs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏪 AI Marketplace v2</h3>
    <div className="text-sm">{active}/{marketplaces} active · {listings.toLocaleString()} listings · {publishers} publishers · {installs.toLocaleString()} installs</div>
  </div>);
}
