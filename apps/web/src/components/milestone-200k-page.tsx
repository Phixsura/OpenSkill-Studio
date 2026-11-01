"use client";

interface MilestoneStats { commits: number; lines: number; files: number;
  services: number; components: number; tests: number; }
interface Milestone200kPageProps { stats: MilestoneStats; modules: string[];
  achievement: string; builder: string; }

export function Milestone200kPage({ stats, modules, achievement, builder }: Milestone200kPageProps) {
  return (
    <div className="max-w-3xl mx-auto text-center space-y-8 py-12">
      <div className="rounded-2xl bg-gradient-to-br from-yellow-500 via-orange-500 to-red-500 p-10 text-white">
        <p className="text-6xl mb-4">🏆</p>
        <h1 className="text-4xl font-black mb-3">200,000 LINES</h1>
        <p className="text-xl opacity-90">OpenSkill Developer Platform</p>
        <p className="text-sm opacity-75 mt-2">{achievement}</p>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {Object.entries(stats).map(([key, val]) => (
          <div key={key} className="rounded-xl border-2 border-yellow-200 dark:border-yellow-800 p-5">
            <p className="text-3xl font-black text-yellow-600">{val.toLocaleString()}</p>
            <p className="text-sm text-gray-400 capitalize">{key}</p>
          </div>
        ))}
      </div>
      <div className="rounded-xl border dark:border-gray-700 p-6">
        <h3 className="font-bold mb-4 text-lg">🏗️ 10 Platform Modules</h3>
        <div className="flex flex-wrap gap-2 justify-center">
          {modules.map(m => (
            <span key={m} className="text-sm px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-400 font-medium">
              {m}
            </span>
          ))}
        </div>
      </div>
      <div className="rounded-xl bg-green-50 dark:bg-green-900/20 p-6">
        <p className="text-2xl font-bold text-green-700 dark:text-green-400">✅ FULLY OPERATIONAL</p>
        <p className="text-sm text-gray-500 mt-2">Built with {builder}</p>
      </div>
    </div>
  );
}
