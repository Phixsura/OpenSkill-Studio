"use client";
export function FleetApiTransformV9Panel({ transforms, active }: { transforms: number; active: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 API Transform v9</h3>
    <div className="text-sm">{transforms} transforms · {active} active</div>
  </div>);
}
