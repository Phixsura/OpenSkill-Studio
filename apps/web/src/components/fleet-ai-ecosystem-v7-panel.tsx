"use client";
export function FleetAiEcosystemV7Panel({ trackers, active, plugins, integrations, listings, developers }: { trackers: number; active: number; plugins: number; integrations: number; listings: number; developers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌿 AI Ecosystem v7</h3>
    <div className="text-sm">{active}/{trackers} active · {plugins.toLocaleString()} plugins · {integrations.toLocaleString()} integrations · {developers.toLocaleString()} devs</div>
  </div>);
}
