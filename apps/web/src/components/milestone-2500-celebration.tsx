"use client";

interface Milestone2500Props { stats: { commits: number; lines: number; files: number;
  services: number; components: number; tests: number; modules: number }; modules: string[]; }

export function Milestone2500Celebration({ stats, modules }: Milestone2500Props) {
  return (
    <div className="rounded-xl border-2 border-yellow-500 overflow-hidden bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/10 dark:to-amber-900/10">
      <div className="p-6 text-center border-b border-yellow-300 dark:border-yellow-700">
        <div className="text-4xl mb-2">🏆🎊🏆</div>
        <h2 className="text-2xl font-bold text-yellow-700 dark:text-yellow-400">2,500 Commits!</h2>
        <p className="text-sm text-yellow-600 mt-1">OpenSkill Developer Platform</p>
      </div>
      <div className="grid grid-cols-4 gap-px bg-yellow-200 dark:bg-yellow-800">
        {[{ l: "Commits", v: stats.commits.toLocaleString() },
          { l: "Lines", v: `${(stats.lines / 1000).toFixed(0)}K` },
          { l: "Files", v: stats.files.toLocaleString() },
          { l: "Modules", v: String(stats.modules) }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-xl font-bold text-yellow-700 dark:text-yellow-400">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="p-4">
        <div className="text-xs text-gray-400 mb-2 text-center">All Modules Operational</div>
        <div className="flex flex-wrap justify-center gap-1.5">
          {modules.map(m => (
            <span key={m} className="px-2 py-0.5 text-[10px] bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400 rounded-full">✅ {m}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
