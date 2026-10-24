"use client";
export function FleetPrismicPanel({ repos, active, documents, slices }: { repos: number; active: number; documents: number; slices: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 Prismic</h3>
    <div className="text-sm">{active}/{repos} active · {documents.toLocaleString()} docs · {slices} slices</div>
  </div>);
}
