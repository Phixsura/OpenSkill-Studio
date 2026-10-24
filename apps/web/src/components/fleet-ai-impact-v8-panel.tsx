"use client";
export function FleetAiImpactV8Panel({ trackers, active, revenue, savings, productivity }: { trackers: number; active: number; revenue: number; savings: number; productivity: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💎 AI Impact v8</h3>
    <div className="text-sm">{active}/{trackers} active · ${revenue.toLocaleString()} rev · ${savings.toLocaleString()} saved · +{productivity}% prod</div>
  </div>);
}
