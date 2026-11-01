"use client";

interface EngagementScoreCardProps { score: number; tier: string; dauMau: number; featureAdoption: number; apiIntensity: number; }

const TIER_STYLES: Record<string, { color: string; icon: string }> = {
  power: { color: "text-purple-600", icon: "⚡" },
  regular: { color: "text-blue-600", icon: "👤" },
  casual: { color: "text-gray-500", icon: "💤" },
};

export function EngagementScoreCard({ score, tier, dauMau, featureAdoption, apiIntensity }: EngagementScoreCardProps) {
  const style = TIER_STYLES[tier] || TIER_STYLES.regular;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Engagement</h3>
        <span className={`text-sm font-bold ${style.color}`}>{style.icon} {tier}</span>
      </div>
      <p className="mt-2 text-3xl font-bold text-center">{score}</p>
      <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
        <div><p className="font-bold">{dauMau}%</p><p className="text-gray-400">DAU/MAU</p></div>
        <div><p className="font-bold">{featureAdoption}%</p><p className="text-gray-400">Features</p></div>
        <div><p className="font-bold">{apiIntensity}</p><p className="text-gray-400">API Score</p></div>
      </div>
    </div>
  );
}
