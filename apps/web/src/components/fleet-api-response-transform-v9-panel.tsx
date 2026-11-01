"use client";
export function FleetApiResponseTransformV9Panel({ transforms, applied }: { transforms: number; applied: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 Response Transform v9</h3>
    <div className="text-sm">{transforms} transforms · {applied.toLocaleString()} applied</div>
  </div>);
}
