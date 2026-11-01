"use client";
export function FleetApiResponseHeaderV9Panel({ endpoints, hsts }: { endpoints: number; hsts: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Response Header v9</h3>
    <div className="text-sm">{endpoints} endpoints · {hsts} HSTS</div>
  </div>);
}
