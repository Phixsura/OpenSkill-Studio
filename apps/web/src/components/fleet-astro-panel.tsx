"use client";
export function FleetAstroPanel({ sites, deployed, pages, islands }: { sites: number; deployed: number; pages: number; islands: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Astro</h3>
    <div className="text-sm">{deployed}/{sites} deployed · {pages} pages · {islands} islands</div>
  </div>);
}
