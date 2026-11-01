"use client";
export function FleetCloudInventoryV9Panel({ resources, types }: { resources: number; types: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Cloud Inventory v9</h3>
    <div className="text-sm">{resources} resources · {types} types</div>
  </div>);
}
