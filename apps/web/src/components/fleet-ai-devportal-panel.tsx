"use client";
export function FleetAiDevportalPanel({ portals, active, docsPages, apiKeys, developers }: { portals: number; active: number; docsPages: number; apiKeys: number; developers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ AI Dev Portal</h3>
    <div className="text-sm">{active}/{portals} active · {docsPages} docs · {apiKeys.toLocaleString()} keys · {developers.toLocaleString()} devs</div>
  </div>);
}
