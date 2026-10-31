"use client";
export function FleetAiEcoHealthPanel({ monitors, active, plugins, integrations, community, growth }: { monitors: number; active: number; plugins: number; integrations: number; community: number; growth: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌿 AI Ecosystem Health</h3>
    <div className="text-sm">{active}/{monitors} active · {plugins} plugins · {integrations} integrations · {community.toLocaleString()} community · +{growth}%</div>
  </div>);
}
