"use client";
export function FleetBackstagePanel({ total, registered, withTechdocs, coveragePct }: { total: number; registered: number; withTechdocs: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎭 Backstage</h3>
    <div className="text-sm">{registered}/{total} registered ({coveragePct}%) · {withTechdocs} with TechDocs</div>
  </div>);
}
