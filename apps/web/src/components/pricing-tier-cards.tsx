"use client";

interface Tier { id: string; name: string; price: number; billing: string;
  features: string[]; highlighted: boolean; cta: string; annual_monthly: number; }
interface PricingTierCardsProps { tiers: Tier[]; annual: boolean; recommendedId?: string;
  onSelect: (id: string) => void; onToggleBilling: () => void; }

export function PricingTierCards({ tiers, annual, recommendedId, onSelect, onToggleBilling }: PricingTierCardsProps) {
  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Choose Your Plan</h2>
        <div className="mt-2 flex items-center justify-center gap-2 text-sm">
          <span className={!annual ? "font-bold" : "text-gray-400"}>Monthly</span>
          <button onClick={onToggleBilling}
            className={`relative h-6 w-11 rounded-full ${annual ? "bg-blue-600" : "bg-gray-300"}`}>
            <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow ${annual ? "left-[1.375rem]" : "left-0.5"}`} />
          </button>
          <span className={annual ? "font-bold" : "text-gray-400"}>Annual</span>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {tiers.map(t => (
          <div key={t.id} className={`rounded-xl border p-5 ${t.highlighted ? "border-2 border-blue-500 shadow-lg" : "dark:border-gray-700"}`}>
            {t.id === recommendedId && <p className="mb-2 text-center text-xs text-blue-600">✨ Recommended</p>}
            <h3 className="text-lg font-bold">{t.name}</h3>
            <div className="mt-2">
              {t.price >= 0 ? (
                <p className="text-3xl font-black">
                  ${annual && t.annual_monthly > 0 ? t.annual_monthly : t.price}
                  <span className="text-sm font-normal text-gray-400">{t.billing}</span>
                </p>
              ) : (
                <p className="text-xl font-bold">Custom</p>
              )}
            </div>
            <ul className="mt-4 space-y-1.5">
              {t.features.map(f => <li key={f} className="flex gap-1.5 text-sm"><span className="text-green-500">✓</span>{f}</li>)}
            </ul>
            <button onClick={() => onSelect(t.id)}
              className={`mt-4 w-full rounded-lg py-2.5 text-sm font-semibold ${t.highlighted ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
              {t.cta}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
