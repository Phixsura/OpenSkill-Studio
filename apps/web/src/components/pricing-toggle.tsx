"use client";

import { useState } from "react";

interface PricingToggleProps { monthlyPrice: number; annualPrice: number;
  savings: number; savingsPct: number; onBillingChange: (annual: boolean) => void; }

export function PricingToggle({ monthlyPrice, annualPrice, savings, savingsPct, onBillingChange }: PricingToggleProps) {
  const [annual, setAnnual] = useState(false);
  const toggle = () => { setAnnual(!annual); onBillingChange(!annual); };
  return (
    <div className="space-y-3 text-center">
      <div className="flex items-center justify-center gap-3">
        <span className={`text-sm ${!annual ? "font-bold" : "text-gray-400"}`}>Monthly</span>
        <button onClick={toggle}
          className={`relative h-7 w-14 rounded-full ${annual ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"}`}>
          <span className={`absolute top-0.5 h-6 w-6 rounded-full bg-white shadow transition-transform ${annual ? "left-[1.875rem]" : "left-0.5"}`} />
        </button>
        <span className={`text-sm ${annual ? "font-bold" : "text-gray-400"}`}>Annual</span>
        {savingsPct > 0 && (
          <span className="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30">
            Save {savingsPct}%
          </span>
        )}
      </div>
      <div>
        <p className="text-4xl font-black">${annual ? annualPrice : monthlyPrice}<span className="text-lg font-normal text-gray-400">/mo</span></p>
        {annual && <p className="text-xs text-green-500">You save ${savings}/year</p>}
      </div>
    </div>
  );
}
