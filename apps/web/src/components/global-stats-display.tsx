"use client";

interface GlobalStats {
  extensions: number; developers: number; installs: number;
  services: number; tests: number; commits: number;
  avgRating: number; uptime: number;
}

interface Highlight { label: string; value: number; metric: string; }

export function GlobalStatsDisplay({ stats, highlights }: { stats: GlobalStats; highlights: Highlight[] }) {
  const metrics = [
    { label: "Extensions", value: stats.extensions, icon: "📦" },
    { label: "Developers", value: stats.developers.toLocaleString(), icon: "👩‍💻" },
    { label: "Installs", value: stats.installs.toLocaleString(), icon: "📥" },
    { label: "Services", value: stats.services, icon: "⚙️" },
    { label: "Tests", value: stats.tests.toLocaleString(), icon: "✅" },
    { label: "Commits", value: stats.commits.toLocaleString(), icon: "📝" },
    { label: "Rating", value: `★ ${stats.avgRating}`, icon: "⭐" },
    { label: "Uptime", value: `${stats.uptime}%`, icon: "💚" },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🌍 Platform Stats</h2>
      <div className="grid grid-cols-4 gap-2 sm:grid-cols-8">
        {metrics.map((m) => (
          <div key={m.label} className="rounded-lg border dark:border-gray-700 p-2 text-center">
            <span className="text-lg block">{m.icon}</span>
            <span className="font-bold text-sm block">{m.value}</span>
            <span className="text-[10px] text-gray-500">{m.label}</span>
          </div>
        ))}
      </div>
      {highlights.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {highlights.map((h) => (
            <span key={h.label} className="text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 px-2 py-1 rounded-full">
              🏆 {h.label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
