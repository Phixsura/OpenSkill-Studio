"use client";
export function FleetAiPlatformImpactV7Panel({ trackers, active, revenue, savings, productivity, customers }: { trackers: number; active: number; revenue: number; savings: number; productivity: number; customers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💎 AI Platform Impact v7</h3>
    <div className="text-sm">{active}/{trackers} active · ${revenue.toLocaleString()} rev · ${savings.toLocaleString()} saved · +{productivity}% prod · {customers.toLocaleString()} customers</div>
  </div>);
}
