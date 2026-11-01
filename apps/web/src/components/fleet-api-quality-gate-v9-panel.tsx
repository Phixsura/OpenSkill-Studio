"use client";
export function FleetApiQualityGateV9Panel({ gates, blocked }: { gates: number; blocked: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 Quality Gate v9</h3>
    <div className="text-sm">{gates} gates · {blocked} blocked</div>
  </div>);
}
