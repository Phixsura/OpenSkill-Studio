"use client";

interface AppListItemProps { name: string; slug: string; status: string; category: string; installCount: number; healthScore: number; needsAttention: boolean; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊" };

export function AppListItem({ name, slug, status, category, installCount, healthScore, needsAttention }: AppListItemProps) {
  return (
    <a href={`/dashboard/developer/apps/${slug}`}
      className={`flex items-center gap-3 rounded-lg border p-3 transition hover:border-blue-400 ${needsAttention ? "border-red-200 dark:border-red-800" : "border-gray-200 dark:border-gray-700"}`}>
      <span className="text-xl">{ICONS[category] ?? "📦"}</span>
      <div className="flex-1">
        <span className="font-semibold">{name}</span>
        <span className="ml-2 text-xs text-gray-500">{status}</span>
      </div>
      <span className="text-xs text-gray-400">📥 {installCount}</span>
      <span className={`text-xs ${healthScore >= 90 ? "text-green-600" : "text-yellow-600"}`}>❤️ {healthScore}%</span>
      {needsAttention && <span className="text-xs text-red-500">⚠️</span>}
    </a>
  );
}
