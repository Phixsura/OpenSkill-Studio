"use client";

interface Stats { commits: number; lines: number; files: number; backend_services: number;
  frontend_components: number; test_files: number; }
interface Milestone4kCelebrationProps { stats: Stats; achievement: string; version: string; }

export function Milestone4kCelebration({ stats, achievement, version }: Milestone4kCelebrationProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-gradient-to-br from-yellow-500 via-orange-500 to-red-500 p-10 text-center text-white">
        <p className="text-6xl">🏆</p>
        <h1 className="mt-3 text-4xl font-black">4,000 FILES!</h1>
        <p className="mt-2 text-xl">{achievement}</p>
        <p className="mt-1 opacity-70">v{version} — Fully Operational</p>
      </div>
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {[
          { label: "Commits", value: stats.commits, icon: "📝" },
          { label: "Lines", value: stats.lines, icon: "📏" },
          { label: "Files", value: stats.files, icon: "📁" },
          { label: "Services", value: stats.backend_services, icon: "⚙️" },
          { label: "Components", value: stats.frontend_components, icon: "🧩" },
          { label: "Tests", value: stats.test_files, icon: "🧪" },
        ].map(s => (
          <div key={s.label} className="rounded-lg border-2 border-yellow-400 p-3 text-center dark:border-yellow-600">
            <span className="text-xl">{s.icon}</span>
            <p className="mt-1 text-xl font-bold">{s.value.toLocaleString()}</p>
            <p className="text-[10px] text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
