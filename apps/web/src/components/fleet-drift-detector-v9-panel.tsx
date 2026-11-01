"use client";
export function FleetDriftDetectorV9Panel({ resources, drifted }: { resources: number; drifted: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Drift Detector v9</h3>
    <div className="text-sm">{resources} resources · {drifted} drifted</div>
  </div>);
}
