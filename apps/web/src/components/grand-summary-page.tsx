"use client";

interface GrandSummaryStats { commits: number; lines: number; files: number;
  services: number; components: number; tests: number; }
interface GrandSummaryPageProps { milestone: string; stats: GrandSummaryStats;
  modules: string[]; status: string; achievement: string; }

export function GrandSummaryPage({ milestone, stats, modules, status, achievement }: GrandSummaryPageProps) {
  return (
    <div className="max-w-2xl mx-auto text-center space-y-6">
      <div className="rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 p-8 text-white">
        <p className="text-5xl mb-2">🏆</p>
        <h1 className="text-3xl font-bold mb-2">{milestone}</h1>
        <p className="text-lg opacity-90">OpenSkill Developer Platform</p>
        <p className="text-sm opacity-75 mt-1">{achievement}</p>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {Object.entries(stats).map(([key, val]) => (
          <div key={key} className="rounded-xl border p-4 dark:border-gray-700">
            <p className="text-2xl font-bold">{val.toLocaleString()}</p>
            <p className="text-xs text-gray-400 capitalize">{key}</p>
          </div>
        ))}
      </div>
      <div className="rounded-xl border p-5 dark:border-gray-700">
        <h3 className="font-semibold mb-3">📦 Platform Modules</h3>
        <div className="flex flex-wrap gap-2 justify-center">
          {modules.map(m => (
            <span key={m} className="text-xs px-3 py-1.5 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400">
              {m}
            </span>
          ))}
        </div>
      </div>
      <div className="rounded-xl bg-green-50 dark:bg-green-900/20 p-4 text-green-700 dark:text-green-400 font-bold text-lg">
        ✅ {status}
      </div>
    </div>
  );
}
