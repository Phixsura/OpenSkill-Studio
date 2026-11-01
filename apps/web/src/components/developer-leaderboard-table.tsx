"use client";

interface LeaderboardEntry { rank: number; developer_id: string; display_name: string; value: number; change: number; }
interface DeveloperLeaderboardTableProps { metric: string; period: string; entries: LeaderboardEntry[]; }

const medals = ["🥇", "🥈", "🥉"];
const metricLabels: Record<string, string> = { installs: "Installs", revenue: "Revenue", rating: "Rating", apps_published: "Apps", reviews_received: "Reviews" };

export function DeveloperLeaderboardTable({ metric, period, entries }: DeveloperLeaderboardTableProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Leaderboard</h2>
        <div className="flex gap-2 text-xs text-gray-400">
          <span>{metricLabels[metric] ?? metric}</span>
          <span>·</span>
          <span>{period.replace("_", " ")}</span>
        </div>
      </div>
      <div className="space-y-1.5">
        {entries.map(e => (
          <div key={e.developer_id} className={`flex items-center gap-3 rounded-lg border p-3 dark:border-gray-700 ${e.rank <= 3 ? "bg-yellow-50/50 dark:bg-yellow-900/5" : ""}`}>
            <span className="w-8 text-center text-lg">{e.rank <= 3 ? medals[e.rank - 1] : `#${e.rank}`}</span>
            <span className="flex-1 font-medium">{e.display_name}</span>
            <div className="text-right">
              <span className="font-bold">{metric === "revenue" ? `$${e.value.toLocaleString()}` : e.value.toLocaleString()}</span>
              {e.change !== 0 && (
                <span className={`ml-1 text-xs ${e.change > 0 ? "text-green-500" : "text-red-500"}`}>
                  {e.change > 0 ? "↑" : "↓"}{Math.abs(e.change)}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
