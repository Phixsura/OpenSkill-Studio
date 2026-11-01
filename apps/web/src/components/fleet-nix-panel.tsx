"use client";
export function FleetNixPanel({ total, usingNix, reproducible, adoptionPct }: { total: number; usingNix: number; reproducible: number; adoptionPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">❄️ Nix</h3>
    <div className="text-sm">{usingNix}/{total} Nix ({adoptionPct}%) · {reproducible} reproducible</div>
  </div>);
}
