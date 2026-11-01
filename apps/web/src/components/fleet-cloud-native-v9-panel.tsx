"use client";
export function FleetCloudNativeV9Panel({ workloads, maturity }: { workloads: number; maturity: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Cloud Native v9</h3>
    <div className="text-sm">{workloads} workloads · {maturity}/5 maturity</div>
  </div>);
}
