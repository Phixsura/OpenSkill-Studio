"use client";
export function FleetApiProductHealthV9Panel({ products, adoption }: { products: number; adoption: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 Product Health v9</h3>
    <div className="text-sm">{products} products · {adoption}% adoption</div>
  </div>);
}
