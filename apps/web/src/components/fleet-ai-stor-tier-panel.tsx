"use client";
export function FleetAiStorTierPanel({ tiers, active, hot, warm, cold, saved }: { tiers: number; active: number; hot: number; warm: number; cold: number; saved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Storage Tiering</h3>
    <div className="text-sm">{active}/{tiers} active · 🔥{hot}TB hot · 🌡️{warm}TB warm · ❄️{cold}TB cold · {saved}% saved</div>
  </div>);
}
