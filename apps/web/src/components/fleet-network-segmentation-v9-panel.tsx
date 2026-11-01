"use client";
export function FleetNetworkSegmentationV9Panel({ segments, violations }: { segments: number; violations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Network Segmentation v9</h3>
    <div className="text-sm">{segments} segments · {violations} violations</div>
  </div>);
}
