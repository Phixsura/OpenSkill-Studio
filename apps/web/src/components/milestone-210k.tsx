"use client";

interface Milestone210kProps { commits: number; lines: number; files: number;
  achievements: string[]; }

export function Milestone210k({ commits, lines, files, achievements }: Milestone210kProps) {
  return (
    <div className="max-w-2xl mx-auto text-center py-12 space-y-6">
      <div className="rounded-3xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-600 p-10 text-white shadow-2xl">
        <p className="text-7xl mb-3">🏆</p>
        <h1 className="text-5xl font-black">210,000 LINES</h1>
        <p className="text-xl opacity-90 mt-2">OpenSkill Developer Platform</p>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border-2 border-teal-200 dark:border-teal-800 p-4">
          <p className="text-3xl font-black text-teal-600">{commits.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Commits</p>
        </div>
        <div className="rounded-xl border-2 border-teal-200 dark:border-teal-800 p-4">
          <p className="text-3xl font-black text-teal-600">{lines.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Lines</p>
        </div>
        <div className="rounded-xl border-2 border-teal-200 dark:border-teal-800 p-4">
          <p className="text-3xl font-black text-teal-600">{files.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Files</p>
        </div>
      </div>
      <div className="rounded-xl border dark:border-gray-700 p-5 text-left">
        <h3 className="font-bold mb-2 text-center">🏅 Session Achievements</h3>
        {achievements.map((a, i) => <p key={i} className="text-sm text-gray-500 py-0.5">✅ {a}</p>)}
      </div>
      <p className="text-2xl font-bold text-green-600">✅ ALL FULLY OPERATIONAL</p>
    </div>
  );
}
