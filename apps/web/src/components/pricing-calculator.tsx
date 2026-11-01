"use client";
import { useState } from "react";

interface PricingTier { name: string; monthlyPrice: number; features: string[]; recommended?: boolean; }

export function PricingCalculator({ tiers, onSelect }: { tiers: PricingTier[]; onSelect?: (tier: string) => void }) {
  const [annual, setAnnual] = useState(false);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">💰 Pricing</h2>
        <label className="flex items-center gap-2 text-sm">
          <span className={!annual ? "font-bold" : ""}>Monthly</span>
          <button onClick={() => setAnnual(!annual)} className={`w-10 h-5 rounded-full ${annual ? "bg-blue-600" : "bg-gray-300"} relative`}>
            <span className={`absolute w-4 h-4 bg-white rounded-full top-0.5 transition-all ${annual ? "left-5.5" : "left-0.5"}`} />
          </button>
          <span className={annual ? "font-bold" : ""}>Annual <span className="text-green-600 text-xs">-20%</span></span>
        </label>
      </div>
      <div className="grid gap-3 grid-cols-1 sm:grid-cols-3">
        {tiers.map((t) => {
          const price = annual ? Math.round(t.monthlyPrice * 0.8) : t.monthlyPrice;
          return (
            <div key={t.name} className={`rounded-xl border-2 p-4 ${t.recommended ? "border-blue-500" : "dark:border-gray-700"}`}>
              {t.recommended && <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">Recommended</span>}
              <h3 className="font-bold text-lg mt-1">{t.name}</h3>
              <div className="mt-2"><span className="text-2xl font-bold">${price}</span><span className="text-gray-500">/mo</span></div>
              <ul className="mt-3 space-y-1">{t.features.map((f) => <li key={f} className="text-sm text-gray-600">✓ {f}</li>)}</ul>
              <button onClick={() => onSelect?.(t.name)} className="mt-3 w-full text-sm bg-blue-600 text-white py-2 rounded-lg">Select</button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
