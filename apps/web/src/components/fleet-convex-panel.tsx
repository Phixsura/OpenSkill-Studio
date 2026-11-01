"use client";
export function FleetConvexPanel({ projects, deployed, functions, documents }: { projects: number; deployed: number; functions: number; documents: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔺 Convex</h3>
    <div className="text-sm">{deployed}/{projects} deployed · {functions} fns · {documents.toLocaleString()} docs</div>
  </div>);
}
