"use client";
export function FleetApiCompressionV9Panel({ endpoints, saved }: { endpoints: number; saved: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗜️ API Compression v9</h3>
    <div className="text-sm">{endpoints} endpoints · {saved} MB saved</div>
  </div>);
}
