"use client";

interface BundleApp { id: string; name: string; price: number; }
interface BundlePricingCardProps { name: string; apps: BundleApp[]; bundlePrice: number;
  individualTotal: number; savings: number; discountPct: number; onBuy: () => void; }

export function BundlePricingCard({ name, apps, bundlePrice, individualTotal, savings, discountPct, onBuy }: BundlePricingCardProps) {
  return (
    <div className="rounded-lg border-2 border-blue-500 p-5">
      <div className="text-center">
        <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-bold text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
          SAVE {discountPct}%
        </span>
        <h2 className="mt-2 text-xl font-bold">{name}</h2>
      </div>
      <div className="mt-3 space-y-1.5">
        {apps.map(a => (
          <div key={a.id} className="flex justify-between text-sm">
            <span>{a.name}</span>
            <span className="text-gray-400 line-through">${a.price.toFixed(2)}</span>
          </div>
        ))}
      </div>
      <div className="mt-4 border-t pt-3 dark:border-gray-700">
        <div className="flex justify-between text-sm text-gray-400">
          <span>Individual total</span><span>${individualTotal.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm text-green-600">
          <span>You save</span><span>-${savings.toFixed(2)}</span>
        </div>
        <div className="mt-1 flex justify-between text-lg font-bold">
          <span>Bundle price</span><span>${bundlePrice.toFixed(2)}</span>
        </div>
      </div>
      <button onClick={onBuy} className="mt-3 w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white">
        Buy Bundle
      </button>
    </div>
  );
}
