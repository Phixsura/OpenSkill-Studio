"use client";
export function FleetConfigDriftDetectorV9Panel({ configs, drifted }: { configs: number; drifted: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ Config Drift Detector v9</h3>
    <div className="text-sm">{configs} configs · {drifted} drifted</div>
  </div>);
}
