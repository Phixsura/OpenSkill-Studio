"use client";
export function FleetTechdocsPanel({ total, withTechdocs, buildsOk, coveragePct }: { total: number; withTechdocs: number; buildsOk: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 TechDocs</h3>
    <div className="text-sm">{withTechdocs}/{total} documented ({coveragePct}%) · {buildsOk} builds OK</div>
  </div>);
}
