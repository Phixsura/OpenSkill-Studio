"use client";
export function FleetNuxtPanel({ apps, deployed, pages, presets }: { apps: number; deployed: number; pages: number; presets: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟢 Nuxt</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {pages} pages · {presets} presets</div>
  </div>);
}
