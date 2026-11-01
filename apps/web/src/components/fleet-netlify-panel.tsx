"use client";
export function FleetNetlifyPanel({ sites, published, deploys, functions }: { sites: number; published: number; deploys: number; functions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Netlify</h3>
    <div className="text-sm">{published}/{sites} published · {deploys} deploys · {functions} functions</div>
  </div>);
}
