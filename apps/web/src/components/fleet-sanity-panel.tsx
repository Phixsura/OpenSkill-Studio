"use client";
export function FleetSanityPanel({ projects, active, documents, datasets }: { projects: number; active: number; documents: number; datasets: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 Sanity</h3>
    <div className="text-sm">{active}/{projects} active · {documents.toLocaleString()} docs · {datasets} datasets</div>
  </div>);
}
