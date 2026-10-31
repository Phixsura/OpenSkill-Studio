"use client";

interface FeatureInfo { feature_name: string; adoption_pct: number; adopters: number; total_consumers: number; adoption_tier: string; }
interface Props { features: FeatureInfo[]; tierCounts: Record<string, number>; appName: string; }

const tierColor: Record<string, string> = { mainstream: "text-green-600", early_majority: "text-blue-600", early_adopters: "text-purple-600", innovators: "text-orange-600" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoptionCard({ features, tierCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Feature Adoption</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {features.length} features</p>
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(tierCounts).map(([tier, count]) => (
          <span key={tier} className={`text-[10px] font-medium ${tierColor[tier] ?? ""}`}>{tier.replace(/_/g, " ")}: {count}</span>
        ))}
      </div>
      {features.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No adoption data</p>
      ) : (
        <div className="space-y-2">
          {features.slice(0, 5).map((f) => (
            <div key={f.feature_name}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{f.feature_name}</span>
                <span className={tierColor[f.adoption_tier] ?? "text-gray-400"}>{f.adoption_pct}%</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${f.adoption_pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
