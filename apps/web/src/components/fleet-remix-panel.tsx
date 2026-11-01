"use client";
export function FleetRemixPanel({ apps, deployed, loaders, actions }: { apps: number; deployed: number; loaders: number; actions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💿 Remix</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {loaders} loaders · {actions} actions</div>
  </div>);
}
