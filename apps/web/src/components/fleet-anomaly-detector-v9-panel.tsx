"use client";
export function FleetAnomalyDetectorV9Panel({ detectors, anomalies }: { detectors: number; anomalies: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 Anomaly Detector v9</h3>
    <div className="text-sm">{detectors} detectors · {anomalies} anomalies</div>
  </div>);
}
