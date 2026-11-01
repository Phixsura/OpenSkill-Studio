"use client";
export function FleetApiCorsV9Panel({ policies, wildcard }: { policies: number; wildcard: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 API CORS v9</h3>
    <div className="text-sm">{policies} policies · {wildcard} wildcard</div>
  </div>);
}
