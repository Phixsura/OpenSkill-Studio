"use client";
export function FleetAiDataGovV7Panel({ systems, active, datasets, classified, policies, compliance }: { systems: number; active: number; datasets: number; classified: number; policies: number; compliance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Data Gov v7</h3>
    <div className="text-sm">{active}/{systems} active · {datasets.toLocaleString()} datasets · {classified.toLocaleString()} classified · {policies} policies · {compliance}%</div>
  </div>);
}
