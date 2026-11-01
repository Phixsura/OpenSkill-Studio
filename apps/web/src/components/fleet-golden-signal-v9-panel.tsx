"use client";
export function FleetGoldenSignalV9Panel({ services, allOk }: { services: number; allOk: boolean }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✨ Golden Signals v9</h3>
    <div className="text-sm">{services} services · {allOk ? "All OK ✅" : "Issues ⚠️"}</div>
  </div>);
}
