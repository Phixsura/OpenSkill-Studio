"use client";
export function FleetCosmosdbPanel({ accounts, available, consumedRu, regions }: { accounts: number; available: number; consumedRu: number; regions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 Cosmos DB</h3>
    <div className="text-sm">{available}/{accounts} online · {consumedRu.toLocaleString()} RU/s · {regions} regions</div>
  </div>);
}
