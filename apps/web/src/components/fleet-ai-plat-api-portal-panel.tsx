"use client";
export function FleetAiPlatApiPortalPanel({ portals, active, apis, pages, developers, apiKeys }: { portals: number; active: number; apis: number; pages: number; developers: number; apiKeys: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ AI API Portal v2</h3>
    <div className="text-sm">{active}/{portals} active · {apis} APIs · {pages.toLocaleString()} pages · {developers.toLocaleString()} devs · {apiKeys.toLocaleString()} keys</div>
  </div>);
}
