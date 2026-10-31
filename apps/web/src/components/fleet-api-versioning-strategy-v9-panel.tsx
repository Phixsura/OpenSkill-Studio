"use client";
export function FleetApiVersioningStrategyV9Panel({ apis, url }: { apis: number; url: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 API Versioning v9</h3>
    <div className="text-sm">{apis} APIs · {url} URL-versioned</div>
  </div>);
}
