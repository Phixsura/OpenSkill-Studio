"use client";

interface Stats { commits: number; lines: number; files: number; backend_services: number;
  frontend_components: number; test_files: number; security_fixes: number; }
interface Milestone140kHeroProps { stats: Stats; achievement: string; version: string;
  codename: string; tech: string[]; journey: string; }

export function Milestone140kHero({ stats, achievement, version, codename, tech, journey }: Milestone140kHeroProps) {
  return (
    <div className="space-y-8">
      <div className="rounded-2xl bg-gradient-to-br from-yellow-500 via-red-500 to-purple-600 p-10 text-center text-white">
        <p className="text-6xl">🏆</p>
        <h1 className="mt-3 text-5xl font-black">140,000 LINES!</h1>
        <p className="mt-2 text-xl font-medium opacity-80">v{version} — {codename}</p>
        <p className="mt-2 text-sm opacity-60">{journey}</p>
      </div>
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-7">
        {[
          { label: "Commits", value: stats.commits, icon: "📝" },
          { label: "Lines", value: stats.lines, icon: "📏" },
          { label: "Files", value: stats.files, icon: "📁" },
          { label: "Services", value: stats.backend_services, icon: "⚙️" },
          { label: "Components", value: stats.frontend_components, icon: "🧩" },
          { label: "Tests", value: stats.test_files, icon: "🧪" },
          { label: "Sec Fixes", value: stats.security_fixes, icon: "🔒" },
        ].map(s => (
          <div key={s.label} className="rounded-lg border-2 border-yellow-400 p-3 text-center dark:border-yellow-600">
            <span className="text-xl">{s.icon}</span>
            <p className="mt-1 text-xl font-bold">{s.value.toLocaleString()}</p>
            <p className="text-[10px] text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="text-center">
        <p className="text-xs text-gray-400">Built with: {tech.join(" · ")}</p>
        <p className="mt-2 text-lg font-bold">{achievement}</p>
      </div>
    </div>
  );
}
