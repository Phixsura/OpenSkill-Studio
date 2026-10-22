"use client";

interface CategoryStat { category: string; count: number; installs: number; avgHealth: number; }

interface CategoryStatsChartProps { stats: CategoryStat[]; }

const CAT_ICONS: Record<string, string> = {
  connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️",
  ecosystem_source: "🌐", content_pack: "📦", workflow_adapter: "⚡",
};

export function CategoryStatsChart({ stats }: CategoryStatsChartProps) {
  if (stats.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No category data</p>;
  const maxCount = Math.max(...stats.map(s => s.count), 1);

  return (
    <div className="space-y-2">
      {stats.map(s => (
        <div key={s.category} className="flex items-center gap-3">
          <span className="w-6 text-center">{CAT_ICONS[s.category] ?? "📦"}</span>
          <span className="w-28 text-sm capitalize">{s.category.replace(/_/g, " ")}</span>
          <div className="flex-1">
            <div className="h-4 w-full rounded-full bg-gray-200 dark:bg-gray-700">
              <div className="h-4 rounded-full bg-blue-500" style={{ width: `${(s.count / maxCount) * 100}%` }} />
            </div>
          </div>
          <span className="w-16 text-right text-xs text-gray-500">{s.count} apps</span>
          <span className="w-20 text-right text-xs text-gray-500">📥 {s.installs}</span>
        </div>
      ))}
    </div>
  );
}
