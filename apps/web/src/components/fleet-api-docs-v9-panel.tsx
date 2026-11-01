"use client";
export function FleetApiDocsV9Panel({ endpoints, coverage }: { endpoints: number; coverage: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 API Docs v9</h3>
    <div className="text-sm">{endpoints} endpoints · {coverage}% documented</div>
  </div>);
}
