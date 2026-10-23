"use client";

interface Plan { id: string; price: number; interval: string; features: string[];
  featureCount: number; recommended: boolean; }
interface PricingCardsProps { plans: Plan[]; onSelect: (id: string) => void; }

export function PricingCards({ plans, onSelect }: PricingCardsProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {plans.map(p => (
        <div key={p.id}
          className={`rounded-xl border p-5 ${p.recommended ? "border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800" : "dark:border-gray-700"}`}>
          {p.recommended && <span className="mb-2 inline-block rounded-full bg-blue-600 px-2.5 py-0.5 text-xs text-white">Recommended</span>}
          <h3 className="text-lg font-bold capitalize">{p.id}</h3>
          <div className="mt-2">
            <span className="text-3xl font-bold">${p.price}</span>
            <span className="text-sm text-gray-400">/{p.interval}</span>
          </div>
          <ul className="mt-4 space-y-2">
            {p.features.map(f => (
              <li key={f} className="flex items-center gap-2 text-sm">
                <span className="text-green-500">✓</span>{f}
              </li>
            ))}
          </ul>
          <button onClick={() => onSelect(p.id)}
            className={`mt-4 w-full rounded-lg py-2 text-sm font-medium ${p.recommended ? "bg-blue-600 text-white" : "border dark:border-gray-700"}`}>
            {p.price === 0 ? "Get Started" : "Subscribe"}
          </button>
        </div>
      ))}
    </div>
  );
}
