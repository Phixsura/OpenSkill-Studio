"use client";
export function FleetApiMiddlewareV9Panel({ middlewares, overhead }: { middlewares: number; overhead: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 API Middleware v9</h3>
    <div className="text-sm">{middlewares} middlewares · {overhead}ms overhead</div>
  </div>);
}
