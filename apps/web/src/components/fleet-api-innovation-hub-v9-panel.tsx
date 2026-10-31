"use client";
export function FleetApiInnovationHubV9Panel({ experiments, graduated }: { experiments: number; graduated: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💡 Innovation Hub v9</h3>
    <div className="text-sm">{experiments} experiments · {graduated} graduated</div>
  </div>);
}
