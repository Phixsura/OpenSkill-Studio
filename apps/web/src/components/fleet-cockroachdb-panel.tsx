"use client";
export function FleetCockroachdbPanel({ nodes, live, ranges, underReplicated }: { nodes: number; live: number; ranges: number; underReplicated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪳 CockroachDB</h3>
    <div className="text-sm">{live}/{nodes} live · {ranges.toLocaleString()} ranges</div>
    {underReplicated > 0 && <span className="text-xs text-red-500">⚠️ {underReplicated} under-replicated</span>}
  </div>);
}
