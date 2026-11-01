"use client";

interface FeatureInfo { feature_id: string; name: string; adoption_count: number; adoption_pct: number; }
interface Props { features: FeatureInfo[]; totalConsumers: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerFeatureAdoptionCard({ features, totalConsumers, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Feature Adoption</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalConsumers} consumers</p>
      </div>
      {features.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No features tracked</p>
      ) : (
        <div className="space-y-1.5">
          {features.map((f) => (
            <div key={f.feature_id} className="text-[11px]">
              <div className="flex justify-between"><span className="text-gray-700 dark:text-gray-300">{f.name}</span><span className="text-gray-400">{f.adoption_count} ({f.adoption_pct}%)</span></div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800"><div className="h-1 rounded-full bg-blue-500" style={{ width: `${f.adoption_pct}%` }} /></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
