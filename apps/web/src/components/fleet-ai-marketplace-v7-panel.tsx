"use client";
export function FleetAiMarketplaceV7Panel({ marketplaces, active, listings, downloads, publishers, revenue }: { marketplaces: number; active: number; listings: number; downloads: number; publishers: number; revenue: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏪 AI Marketplace v7</h3>
    <div className="text-sm">{active}/{marketplaces} active · {listings.toLocaleString()} listings · {downloads.toLocaleString()} downloads · {publishers.toLocaleString()} publishers</div>
  </div>);
}
