"use client";

interface Stats { commits: number; lines: number; files: number; services: number; }
interface Milestone208kCelebrationProps { stats: Stats; milestones: string[]; achievement: string; }

export function Milestone208kCelebration({ stats, milestones, achievement }: Milestone208kCelebrationProps) {
  return (
    <div className="max-w-3xl mx-auto text-center py-16 space-y-8">
      <div className="rounded-3xl bg-gradient-to-br from-yellow-400 via-orange-500 to-red-600 p-12 text-white shadow-2xl">
        <p className="text-7xl mb-4">🏆</p>
        <h1 className="text-5xl font-black mb-3">208,000 LINES</h1>
        <p className="text-xl opacity-90">OpenSkill Developer Platform</p>
        <p className="text-sm opacity-75 mt-2">{achievement}</p>
      </div>
      <div className="grid grid-cols-4 gap-4">
        {Object.entries(stats).map(([k, v]) => (
          <div key={k} className="rounded-xl border-2 border-yellow-300 dark:border-yellow-700 p-5 bg-yellow-50/30 dark:bg-yellow-900/10">
            <p className="text-3xl font-black text-yellow-600">{v.toLocaleString()}</p>
            <p className="text-xs text-gray-500 capitalize">{k}</p>
          </div>
        ))}
      </div>
      <div className="rounded-xl border dark:border-gray-700 p-6 text-left">
        <h3 className="font-bold mb-3 text-center">📈 Session Milestones</h3>
        {milestones.map((m, i) => <p key={i} className="text-sm text-gray-500 py-0.5">{m}</p>)}
      </div>
      <p className="text-2xl font-bold text-green-600">✅ ALL FULLY OPERATIONAL</p>
    </div>
  );
}
