"use client";

interface TierInfo { tier_id: string; name: string; monthly_limit: number; base_price_cents: number; price_per_request_cents: number; }
interface Props { tiers: TierInfo[]; appName: string; }

const fmtPrice = (cents: number) => `$${(cents / 100).toFixed(2)}`;

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerTierPricingCard({ tiers, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💰 Tier Pricing</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {tiers.length} tiers</p>
      </div>
      {tiers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No pricing tiers</p>
      ) : (
        <div className="space-y-2">
          {tiers.map((t) => (
            <div key={t.tier_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-semibold text-gray-900 dark:text-gray-100">{t.name}</span>
                <span className="text-gray-600 dark:text-gray-400">{fmtPrice(t.base_price_cents)}/mo</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">
                {t.monthly_limit.toLocaleString()} requests · {t.price_per_request_cents}¢/overage
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
