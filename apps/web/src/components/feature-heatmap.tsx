"use client";

interface FeatureHeatmapProps { adoption: Record<string, { users: number; pct: number }>;
  totalUsers: number; features: string[]; }

export function FeatureHeatmap({ adoption, totalUsers, features }: FeatureHeatmapProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔥 Feature Adoption</h3>
        <span className="text-xs text-gray-400">{totalUsers} users</span>
      </div>
      <div className="p-4 space-y-2">
        {features.map(f => {
          const a = adoption[f] ?? { users: 0, pct: 0 };
          const color = a.pct > 70 ? "bg-green-500" : a.pct > 40 ? "bg-yellow-500" : "bg-gray-400";
          return (
            <div key={f}>
              <div className="flex justify-between text-xs mb-0.5">
                <span className="font-medium">{f}</span>
                <span className="text-gray-400">{a.users} users ({a.pct}%)</span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${color}`} style={{ width: `${a.pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
