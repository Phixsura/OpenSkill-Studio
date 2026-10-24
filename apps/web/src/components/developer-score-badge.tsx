"use client";

interface DeveloperScoreBadgeProps { score: number; maxScore: number; tier: string;
  percentile: number; breakdown: Record<string, number>; }

const tierStyle: Record<string, { color: string; icon: string }> = {
  legend: { color: "from-yellow-500 to-amber-600", icon: "👑" },
  expert: { color: "from-purple-500 to-indigo-600", icon: "🌟" },
  rising: { color: "from-blue-500 to-cyan-600", icon: "📈" },
  newcomer: { color: "from-gray-400 to-gray-500", icon: "🌱" },
};

const metricLabels: Record<string, string> = {
  apps_published: "Apps", total_installs: "Installs", avg_rating: "Rating",
  reviews_responded: "Reviews", docs_quality: "Docs", security_clean: "Security",
  active_days_30: "Activity",
};

export function DeveloperScoreBadge({ score, maxScore, tier, percentile, breakdown }: DeveloperScoreBadgeProps) {
  const t = tierStyle[tier] ?? tierStyle.newcomer;
  return (
    <div className="space-y-4">
      <div className={`rounded-xl bg-gradient-to-r ${t.color} p-6 text-center text-white`}>
        <span className="text-3xl">{t.icon}</span>
        <p className="mt-2 text-4xl font-black">{score}</p>
        <p className="text-sm capitalize opacity-80">{tier} · Top {percentile}%</p>
      </div>
      <div className="space-y-1.5">
        {Object.entries(breakdown).map(([key, val]) => (
          <div key={key}>
            <div className="flex justify-between text-xs">
              <span>{metricLabels[key] ?? key}</span>
              <span className="text-gray-400">{val}/{maxScore / Object.keys(breakdown).length}</span>
            </div>
            <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className="h-full rounded-full bg-blue-500"
                style={{ width: `${Math.min((val / 200) * 100, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
