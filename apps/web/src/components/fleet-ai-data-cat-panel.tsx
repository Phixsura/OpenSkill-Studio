"use client";
export function FleetAiDataCatPanel({ catalogs, active, datasets, tags, searches }: { catalogs: number; active: number; datasets: number; tags: number; searches: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 AI Data Catalog</h3>
    <div className="text-sm">{active}/{catalogs} active · {datasets.toLocaleString()} datasets · {tags.toLocaleString()} tags · {searches.toLocaleString()} searches</div>
  </div>);
}
