"use client";

interface TierInfo {
  tier_id: string;
  name: string;
  price_monthly: number;
  features: string[];
  rate_limit: number;
}

interface APIPricingTierCardProps {
  tiers: TierInfo[];
  appName: string;
}

export default function APIPricingTierCard({ tiers, appName }: APIPricingTierCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💎 Pricing Tiers</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{tiers.length} tiers</span>
      </div>

      {tiers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No pricing tiers</p>
      ) : (
        <div className="space-y-2">
          {tiers.map((t) => (
            <div key={t.tier_id} className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{t.name}</span>
                <span className="text-sm font-bold text-gray-900 dark:text-gray-100">${t.price_monthly}/mo</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {t.features.slice(0, 4).map((f) => (
                  <span key={f} className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{f}</span>
                ))}
                {t.features.length > 4 && <span className="text-[9px] text-gray-400">+{t.features.length - 4}</span>}
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{t.rate_limit.toLocaleString()}/min</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
