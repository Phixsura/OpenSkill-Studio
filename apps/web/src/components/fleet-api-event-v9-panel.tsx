"use client";
export function FleetApiEventV9Panel({ types, published }: { types: number; published: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 API Event v9</h3>
    <div className="text-sm">{types} types · {published.toLocaleString()} published</div>
  </div>);
}
