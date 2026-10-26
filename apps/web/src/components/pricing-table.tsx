"use client";

interface Plan { planId: string; name: string; priceCents: number; interval: string; features: string[]; trialDays: number; }

function formatPrice(cents: number, interval: string) {
  if (cents === 0) return "Free";
  const price = `$${(cents / 100).toFixed(2)}`;
  return interval === "one_time" ? price : `${price}/${interval === "monthly" ? "mo" : "yr"}`;
}

export function PricingTable({ plans, onSelect }: { plans: Plan[]; onSelect?: (planId: string) => void }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
      {plans.map((p, i) => {
        const popular = i === 1 && plans.length >= 3;
        return (
          <div key={p.planId} className={`border rounded-xl p-4 space-y-3 ${popular ? "border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800" : "border-gray-200 dark:border-gray-700"}`}>
            {popular && <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">Popular</span>}
            <div>
              <span className="font-bold text-lg block">{p.name}</span>
              <span className="text-2xl font-extrabold">{formatPrice(p.priceCents, p.interval)}</span>
            </div>
            {p.trialDays > 0 && <span className="text-xs text-green-600">{p.trialDays}-day free trial</span>}
            <ul className="space-y-1">
              {p.features.map((f, j) => <li key={j} className="text-sm flex items-center gap-1"><span className="text-green-500">✓</span> {f}</li>)}
            </ul>
            <button onClick={() => onSelect?.(p.planId)}
              className={`w-full py-2 rounded-lg text-sm font-medium ${popular ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
              {p.priceCents === 0 ? "Get Started" : "Subscribe"}
            </button>
          </div>
        );
      })}
    </div>
  );
}
