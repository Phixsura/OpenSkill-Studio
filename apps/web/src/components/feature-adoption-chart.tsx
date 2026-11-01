"use client";

interface FeatureAdoption { feature: string; unique_users: number; adoption_pct: number; }
interface FeatureAdoptionChartProps { features: FeatureAdoption[]; totalUsers: number; }

export function FeatureAdoptionChart({ features, totalUsers }: FeatureAdoptionChartProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Feature Adoption</h3>
        <span className="text-xs text-gray-400">{totalUsers.toLocaleString()} total users</span>
      </div>
      <div className="mt-3 space-y-2">
        {features.map(f => (
          <div key={f.feature}>
            <div className="flex justify-between text-xs">
              <span className="font-medium">{f.feature}</span>
              <span className="text-gray-400">{f.unique_users} users ({f.adoption_pct}%)</span>
            </div>
            <div className="mt-0.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${f.adoption_pct > 50 ? "bg-green-500" : f.adoption_pct > 20 ? "bg-blue-500" : "bg-gray-400"}`}
                style={{ width: `${f.adoption_pct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
