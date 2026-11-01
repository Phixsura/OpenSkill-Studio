"use client";
export function FleetAiMarketplacePanel({ marketplaces, active, listings, installs }: { marketplaces: number; active: number; listings: number; installs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏪 AI Marketplace</h3>
    <div className="text-sm">{active}/{marketplaces} active · {listings} listings · {installs.toLocaleString()} installs</div>
  </div>);
}
