"use client";
export function FleetSvcCatalogPanel({ total, withOwner, withDocs, withRunbook, completenessPct }: { total: number; withOwner: number; withDocs: number; withRunbook: number; completenessPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 Service Catalog</h3>
    <div className="text-sm">{total} services · {completenessPct}% complete</div>
    <div className="text-xs text-gray-400">{withOwner} owned · {withDocs} documented · {withRunbook} runbooked</div>
  </div>);
}
