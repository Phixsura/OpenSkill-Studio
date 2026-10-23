"use client";

interface Tier { id: string; name: string; priceDisplay: string; recommended: boolean;
  features: string[]; featureCount: number; }
interface Faq { q: string; a: string; }
interface PricingPageProps { tiers: Tier[]; faq: Faq[]; onSelect: (id: string) => void; }

export function PricingPage({ tiers, faq, onSelect }: PricingPageProps) {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-extrabold">Simple, transparent pricing</h1>
        <p className="mt-2 text-gray-500">Choose the plan that fits your needs</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        {tiers.map(t => (
          <div key={t.id} className={`rounded-xl border p-5 ${t.recommended ? "border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800" : "dark:border-gray-700"}`}>
            {t.recommended && <span className="mb-2 inline-block rounded-full bg-blue-600 px-2.5 py-0.5 text-xs text-white">Most Popular</span>}
            <h3 className="text-lg font-bold">{t.name}</h3>
            <p className="mt-1 text-2xl font-extrabold">{t.priceDisplay}</p>
            <ul className="mt-4 space-y-2">{t.features.map(f => (
              <li key={f} className="flex items-center gap-2 text-sm"><span className="text-green-500">✓</span>{f}</li>
            ))}</ul>
            <button onClick={() => onSelect(t.id)}
              className={`mt-4 w-full rounded-lg py-2 text-sm font-medium ${t.recommended ? "bg-blue-600 text-white" : "border dark:border-gray-700"}`}>
              {t.priceDisplay === "Free" ? "Get Started" : t.priceDisplay === "Custom" ? "Contact Sales" : "Start Free Trial"}
            </button>
          </div>
        ))}
      </div>
      <div className="mx-auto max-w-2xl">
        <h2 className="text-lg font-bold mb-4">FAQ</h2>
        {faq.map((f, i) => (
          <div key={i} className="border-b py-3 dark:border-gray-800">
            <p className="text-sm font-medium">{f.q}</p>
            <p className="mt-1 text-sm text-gray-500">{f.a}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
