"use client";
export function FleetPagesPanel({ projects, deployed, builds, customDomains }: { projects: number; deployed: number; builds: number; customDomains: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 Pages</h3>
    <div className="text-sm">{deployed}/{projects} deployed · {builds} builds · {customDomains} domains</div>
  </div>);
}
