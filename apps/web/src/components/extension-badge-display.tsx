"use client";

interface Badge {
  id: string;
  name: string;
  icon: string;
  tier: "bronze" | "silver" | "gold" | "platinum";
  description: string;
  earnedAt: string;
}

export function ExtensionBadgeDisplay({
  badges,
  developerName,
  showEarnedDate,
}: {
  badges: Badge[];
  developerName: string;
  showEarnedDate?: boolean;
}) {
  const tierOrder = { platinum: 0, gold: 1, silver: 2, bronze: 3 };
  const sorted = [...badges].sort((a, b) => tierOrder[a.tier] - tierOrder[b.tier]);

  const tierColors: Record<string, { bg: string; border: string; text: string }> = {
    bronze: { bg: "bg-amber-50 dark:bg-amber-900/10", border: "border-amber-300 dark:border-amber-700", text: "text-amber-700 dark:text-amber-300" },
    silver: { bg: "bg-gray-50 dark:bg-gray-800", border: "border-gray-300 dark:border-gray-600", text: "text-gray-600 dark:text-gray-300" },
    gold: { bg: "bg-yellow-50 dark:bg-yellow-900/10", border: "border-yellow-400 dark:border-yellow-600", text: "text-yellow-700 dark:text-yellow-300" },
    platinum: { bg: "bg-purple-50 dark:bg-purple-900/10", border: "border-purple-400 dark:border-purple-600", text: "text-purple-700 dark:text-purple-300" },
  };

  const tierCounts = badges.reduce((acc, b) => {
    acc[b.tier] = (acc[b.tier] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🏅 {developerName}&apos;s Badges</h2>
        <div className="flex gap-2 text-xs">
          {Object.entries(tierCounts).map(([tier, count]) => (
            <span key={tier} className={`px-2 py-0.5 rounded-full ${tierColors[tier]?.bg} ${tierColors[tier]?.text}`}>
              {count} {tier}
            </span>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {sorted.map((badge) => {
          const colors = tierColors[badge.tier];
          return (
            <div key={badge.id} className={`rounded-xl border-2 p-4 text-center ${colors.bg} ${colors.border}`}>
              <div className="text-3xl mb-2">{badge.icon}</div>
              <div className={`font-bold text-sm ${colors.text}`}>{badge.name}</div>
              <div className="text-xs text-gray-500 mt-1">{badge.description}</div>
              {showEarnedDate && (
                <div className="text-xs text-gray-400 mt-1">Earned: {badge.earnedAt}</div>
              )}
              <div className={`text-xs mt-1 uppercase font-semibold ${colors.text}`}>{badge.tier}</div>
            </div>
          );
        })}
      </div>

      {badges.length === 0 && (
        <div className="text-center text-gray-400 py-8">No badges earned yet</div>
      )}
    </div>
  );
}
