"use client";

interface PricingResult { basePrice: number; usageCost: number; totalDisplay: string;
  annualDisplay: string; discount: number; }
interface PricingCalculatorProps { result: PricingResult; onRecalculate: () => void; }

export function PricingCalculator({ result, onRecalculate }: PricingCalculatorProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">💰 Pricing Calculator</h3>
      <div className="space-y-2 text-sm mb-4">
        <div className="flex justify-between"><span>Base price</span><span>${result.basePrice.toFixed(2)}</span></div>
        <div className="flex justify-between"><span>Usage</span><span>${result.usageCost.toFixed(2)}</span></div>
        {result.discount > 0 && (
          <div className="flex justify-between text-green-600"><span>Discount</span><span>-${result.discount.toFixed(2)}</span></div>
        )}
        <div className="flex justify-between font-bold border-t dark:border-gray-700 pt-2">
          <span>Total</span><span>{result.totalDisplay}</span>
        </div>
        <div className="flex justify-between text-xs text-gray-400">
          <span>Annual estimate</span><span>{result.annualDisplay}</span>
        </div>
      </div>
      <button onClick={onRecalculate}
        className="w-full py-2 border rounded text-sm hover:bg-gray-50 dark:hover:bg-gray-800">Recalculate</button>
    </div>
  );
}
