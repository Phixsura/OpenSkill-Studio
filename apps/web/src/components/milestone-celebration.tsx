"use client";

interface MilestoneStats { commits: number; lines: number; files: number;
  services: number; components: number; tests: number; }
interface MilestoneCelebrationProps { milestone: string; achievement: string;
  stats: MilestoneStats; modules: string[]; }

export function MilestoneCelebration({ milestone, achievement, stats, modules }: MilestoneCelebrationProps) {
  return (
    <div className="space-y-6 rounded-xl bg-gradient-to-br from-purple-600 via-blue-600 to-green-500 p-8 text-white">
      <div className="text-center">
        <p className="text-4xl">🏆</p>
        <h1 className="mt-2 text-3xl font-black">{milestone}</h1>
        <p className="mt-1 text-lg opacity-80">{achievement}</p>
      </div>
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {[
          { label: "Commits", value: stats.commits },
          { label: "Lines", value: stats.lines },
          { label: "Files", value: stats.files },
          { label: "Services", value: stats.services },
          { label: "Components", value: stats.components },
          { label: "Tests", value: stats.tests },
        ].map(s => (
          <div key={s.label} className="rounded bg-white/10 p-2 text-center">
            <p className="text-lg font-bold">{s.value.toLocaleString()}</p>
            <p className="text-[10px] opacity-70">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="text-center">
        <p className="text-xs opacity-60">All {modules.length} platform modules operational</p>
        <div className="mt-1 flex flex-wrap justify-center gap-1">
          {modules.map(m => (
            <span key={m} className="rounded-full bg-white/15 px-2 py-0.5 text-[10px]">✅ {m}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
