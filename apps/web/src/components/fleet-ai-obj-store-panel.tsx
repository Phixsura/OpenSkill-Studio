"use client";
export function FleetAiObjStorePanel({ stores, active, objects, sizeTb, ops }: { stores: number; active: number; objects: number; sizeTb: number; ops: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Object Storage</h3>
    <div className="text-sm">{active}/{stores} active · {objects.toLocaleString()} objects · {sizeTb}TB · {ops.toLocaleString()} ops</div>
  </div>);
}
