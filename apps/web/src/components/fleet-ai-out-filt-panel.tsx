"use client";
export function FleetAiOutFiltPanel({ filters, active, filtered, blocked, rules }: { filters: number; active: number; filtered: number; blocked: number; rules: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Output Filter v2</h3>
    <div className="text-sm">{active}/{filters} active · {filtered.toLocaleString()} filtered · {blocked.toLocaleString()} blocked · {rules} rules</div>
  </div>);
}
