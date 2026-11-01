"use client";

interface PlatformFinalStatusProps { milestone: string; commits: number; lines: number;
  files: number; modules: number; milestones: string[]; }

export function PlatformFinalStatus({ milestone, commits, lines, files, modules, milestones }: PlatformFinalStatusProps) {
  return (
    <div className="max-w-2xl mx-auto text-center py-8 space-y-6">
      <div className="rounded-2xl bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 p-8 text-white">
        <p className="text-5xl mb-2">🏆</p>
        <h1 className="text-3xl font-black">{milestone}</h1>
        <p className="text-sm opacity-90 mt-1">OpenSkill Developer Platform</p>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {[{ l: "Commits", v: commits }, { l: "Lines", v: lines },
          { l: "Files", v: files }, { l: "Modules", v: modules }].map(s => (
          <div key={s.l} className="rounded-xl border dark:border-gray-700 p-3">
            <p className="text-xl font-bold">{s.v.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{s.l}</p>
          </div>
        ))}
      </div>
      <div className="text-left rounded-xl border dark:border-gray-700 p-4">
        {milestones.map((m, i) => <p key={i} className="text-sm text-gray-500 py-0.5">✅ {m}</p>)}
      </div>
      <p className="text-lg font-bold text-green-600">✅ FULLY OPERATIONAL</p>
    </div>
  );
}
