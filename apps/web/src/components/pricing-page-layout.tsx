"use client";

import { useState } from "react";

interface Plan { id: string; name: string; display_price: number; highlighted: boolean;
  features: string[]; cta: string; is_current: boolean; savings_pct: number; }
interface Faq { q: string; a: string; }
interface PricingPageLayoutProps { plans: Plan[]; faq: Faq[]; trialDays: number;
  onSelectPlan: (planId: string) => void; }

export function PricingPageLayout({ plans, faq, trialDays, onSelectPlan }: PricingPageLayoutProps) {
  const [annual, setAnnual] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const fmt = (cents: number) => cents < 0 ? "Custom" : cents === 0 ? "Free" : `$${(cents / 100).toFixed(0)}`;

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Simple, transparent pricing</h1>
        <p className="mt-2 text-sm text-gray-500">{trialDays}-day free trial on paid plans</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {plans.map(p => (
          <div key={p.id} className={`rounded-xl border p-5 ${p.highlighted ? "border-blue-500 ring-2 ring-blue-200" : "border-gray-200 dark:border-gray-700"} ${p.is_current ? "bg-blue-50 dark:bg-blue-900/10" : ""}`}>
            <h3 className="text-lg font-bold">{p.name}</h3>
            <p className="mt-1"><span className="text-3xl font-bold">{fmt(p.display_price)}</span>
              {p.display_price > 0 && <span className="text-sm text-gray-400">/mo</span>}</p>
            {p.savings_pct > 0 && <p className="text-xs text-green-600">Save {p.savings_pct}%</p>}
            <ul className="mt-4 space-y-1.5">{p.features.map((f, i) => <li key={i} className="flex items-center gap-1.5 text-sm"><span className="text-green-500">✓</span>{f}</li>)}</ul>
            <button onClick={() => onSelectPlan(p.id)} disabled={p.is_current}
              className={`mt-4 w-full rounded-lg py-2 text-sm font-medium ${p.highlighted ? "bg-blue-600 text-white" : "border border-gray-300"} disabled:opacity-50`}>
              {p.is_current ? "Current Plan" : p.cta}
            </button>
          </div>
        ))}
      </div>
      <div className="mx-auto max-w-2xl">
        <h2 className="text-xl font-bold text-center">FAQ</h2>
        <div className="mt-4 space-y-2">
          {faq.map((f, i) => (
            <div key={i} className="rounded-lg border border-gray-200 dark:border-gray-700">
              <button onClick={() => setOpenFaq(openFaq === i ? null : i)}
                className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium">
                {f.q} <span>{openFaq === i ? "−" : "+"}</span>
              </button>
              {openFaq === i && <p className="px-4 pb-3 text-sm text-gray-500">{f.a}</p>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
