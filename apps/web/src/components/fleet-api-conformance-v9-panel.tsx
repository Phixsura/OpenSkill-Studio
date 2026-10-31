"use client";
export function FleetApiConformanceV9Panel({ tests, violations }: { tests: number; violations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ API Conformance v9</h3>
    <div className="text-sm">{tests} tests · {violations} violations</div>
  </div>);
}
