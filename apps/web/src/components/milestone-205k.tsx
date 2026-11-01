"use client";

interface Milestone205kProps { stats: Record<string, number>; achievement: string; }

export function Milestone205k({ stats, achievement }: Milestone205kProps) {
  return (
    <div className="max-w-2xl mx-auto text-center py-12 space-y-6">
      <div className="rounded-2xl bg-gradient-to-br from-yellow-500 via-orange-500 to-red-500 p-10 text-white">
        <p className="text-6xl mb-3">🏆</p>
        <h1 className="text-4xl font-black">205,000 LINES</h1>
        <p className="text-lg opacity-90 mt-2">OpenSkill Developer Platform</p>
        <p className="text-sm opacity-75 mt-1">{achievement}</p>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {Object.entries(stats).map(([k, v]) => (
          <div key={k} className="rounded-xl border-2 border-yellow-200 dark:border-yellow-800 p-4">
            <p className="text-2xl font-black text-yellow-600">{v.toLocaleString()}</p>
            <p className="text-xs text-gray-400 capitalize">{k}</p>
          </div>
        ))}
      </div>
      <p className="text-xl font-bold text-green-600">✅ FULLY OPERATIONAL</p>
    </div>
  );
}
