"use client";
export function FleetContentDeliveryV9Panel({ assets, saved }: { assets: number; saved: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Content Delivery v9</h3>
    <div className="text-sm">{assets} assets · {saved} GB saved</div>
  </div>);
}
