"use client";

interface PricingPlanCardProps { name: string; priceDisplay: string; billing: string;
  features: string[]; cta: string; recommended: boolean; popular: boolean;
  onSelect: () => void; }

export function PricingPlanCard({ name, priceDisplay, billing, features, cta,
  recommended, popular, onSelect }: PricingPlanCardProps) {
  return (
    <div className={`relative rounded-xl border p-6 ${recommended ? "border-2 border-blue-500 shadow-lg" : "dark:border-gray-700"}`}>
      {popular && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-3 py-0.5 text-xs font-bold text-white">
          Most Popular
        </span>
      )}
      <h3 className="text-lg font-bold">{name}</h3>
      <div className="mt-2">
        <span className="text-4xl font-black">{priceDisplay}</span>
        {priceDisplay !== "Free" && priceDisplay !== "Custom" && (
          <span className="text-sm text-gray-400">{billing}</span>
        )}
      </div>
      <ul className="mt-4 space-y-2">
        {features.map(f => (
          <li key={f} className="flex items-center gap-2 text-sm">
            <span className="text-green-500">✓</span> {f}
          </li>
        ))}
      </ul>
      <button onClick={onSelect}
        className={`mt-6 w-full rounded-lg py-2.5 text-sm font-semibold ${recommended ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
        {cta}
      </button>
    </div>
  );
}
