"use client";

interface Plan { id: string; label: string; price_cents: number; features: string[]; cta: string; highlighted: boolean; }
interface PricingTableCardProps { plans: Plan[]; currentPlan?: string; onSelect: (planId: string) => void; annual?: boolean; }

export function PricingTableCard({ plans, currentPlan, onSelect, annual }: PricingTableCardProps) {
  const formatPrice = (cents: number) => cents < 0 ? "Custom" : cents === 0 ? "Free" : `$${(cents / 100).toFixed(0)}`;
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {plans.map(p => (
        <div key={p.id} className={`rounded-xl border p-5 ${p.highlighted ? "border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800" : "border-gray-200 dark:border-gray-700"} ${currentPlan === p.id ? "bg-blue-50 dark:bg-blue-900/10" : ""}`}>
          <h3 className="text-lg font-bold">{p.label}</h3>
          <p className="mt-1">
            <span className="text-3xl font-bold">{formatPrice(p.price_cents)}</span>
            {p.price_cents > 0 && <span className="text-sm text-gray-400">/mo</span>}
          </p>
          {annual && p.price_cents > 0 && <p className="text-xs text-green-600">Save ~17% annually</p>}
          <ul className="mt-4 space-y-1.5">
            {p.features.map((f, i) => <li key={i} className="flex items-center gap-1.5 text-sm"><span className="text-green-500">✓</span>{f}</li>)}
          </ul>
          <button onClick={() => onSelect(p.id)}
            className={`mt-4 w-full rounded-lg py-2 text-sm font-medium ${p.highlighted ? "bg-blue-600 text-white" : "border border-gray-300 dark:border-gray-600"}`}>
            {currentPlan === p.id ? "Current Plan" : p.cta}
          </button>
        </div>
      ))}
    </div>
  );
}
