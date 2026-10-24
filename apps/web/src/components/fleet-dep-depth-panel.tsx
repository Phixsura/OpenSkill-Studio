"use client";
export function FleetDepDepthPanel({ services, maxDepth, avgDepth, tooDeep, manageable }: { services: number; maxDepth: number; avgDepth: number; tooDeep: number; manageable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌳 Dep Tree Depth</h3>
    <div className="text-sm">max {maxDepth} · avg {avgDepth} · {services} services</div>
    {!manageable && <span className="text-xs text-yellow-600">⚠️ {tooDeep} too deep</span>}
  </div>);
}
