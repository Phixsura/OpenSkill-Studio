"use client";

interface PricingTier {
  id: string;
  name: string;
  price: number; // cents, 0 = free
  currency: string;
  period: "monthly" | "yearly" | "one_time" | "free";
  features: string[];
  highlighted: boolean;
  cta: string;
}

export function ExtensionPricingCard({
  tiers,
  extensionName,
  onSelect,
}: {
  tiers: PricingTier[];
  extensionName: string;
  onSelect?: (tierId: string) => void;
}) {
  const formatPrice = (cents: number, currency: string) => {
    if (cents === 0) return "Free";
    return `${currency === "USD" ? "$" : currency}${(cents / 100).toFixed(2)}`;
  };

  const periodLabel = (p: string) => {
    if (p === "monthly") return "/mo";
    if (p === "yearly") return "/yr";
    if (p === "one_time") return " once";
    return "";
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-center">💎 {extensionName} Plans</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tiers.map((tier) => (
          <div
            key={tier.id}
            className={`rounded-xl border-2 p-5 space-y-4 ${
              tier.highlighted
                ? "border-blue-500 shadow-lg relative"
                : "border-gray-200 dark:border-gray-700"
            }`}
          >
            {tier.highlighted && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs px-3 py-0.5 rounded-full">
                Popular
              </div>
            )}

            <div className="text-center">
              <h3 className="font-bold text-lg">{tier.name}</h3>
              <div className="mt-2">
                <span className="text-3xl font-black">
                  {formatPrice(tier.price, tier.currency)}
                </span>
                <span className="text-sm text-gray-500">{periodLabel(tier.period)}</span>
              </div>
            </div>

            <ul className="space-y-2">
              {tier.features.map((feat, i) => (
                <li key={i} className="flex items-center gap-2 text-sm">
                  <span className="text-green-500">✓</span>
                  <span>{feat}</span>
                </li>
              ))}
            </ul>

            <button
              onClick={() => onSelect?.(tier.id)}
              className={`w-full rounded-lg py-2 text-sm font-semibold ${
                tier.highlighted
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "border dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}
            >
              {tier.cta}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
