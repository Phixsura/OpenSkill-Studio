"use client";
interface FeatureAdoption { feature: string; uniqueUsers: number; adoptionPct: number; }
interface FeatAdoptPanelProps { features: FeatureAdoption[]; totalUsers: number; }
export function FeatAdoptPanel({ features, totalUsers }: FeatAdoptPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Feature Adoption</h3>
        <span className="text-xs text-gray-400">{features.length} features · {totalUsers.toLocaleString()} users</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {features.map(f => (
          <div key={f.feature} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{f.feature}</span>
              <span className="text-gray-400">{f.uniqueUsers} users ({f.adoptionPct}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${f.adoptionPct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
