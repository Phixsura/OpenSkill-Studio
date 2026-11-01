"use client";
export function FleetObservablePanel({ notebooks, published, cells, views }: { notebooks: number; published: number; cells: number; views: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ Observable</h3>
    <div className="text-sm">{published}/{notebooks} published · {cells} cells · {views.toLocaleString()} views</div>
  </div>);
}
