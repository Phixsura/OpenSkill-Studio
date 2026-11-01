"use client";
export function FleetHopsworksPanel({ clusters, running, featureGroups, models }: { clusters: number; running: number; featureGroups: number; models: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏭 Hopsworks</h3>
    <div className="text-sm">{running}/{clusters} running · {featureGroups} FGs · {models} models</div>
  </div>);
}
