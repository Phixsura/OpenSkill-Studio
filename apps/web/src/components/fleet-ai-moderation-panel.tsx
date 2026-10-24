"use client";
export function FleetAiModerationPanel({ services, active, items, flagged, flagRate }: { services: number; active: number; items: number; flagged: number; flagRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Moderation</h3>
    <div className="text-sm">{active}/{services} active · {items.toLocaleString()} items · {flagged.toLocaleString()} flagged ({flagRate}%)</div>
  </div>);
}
