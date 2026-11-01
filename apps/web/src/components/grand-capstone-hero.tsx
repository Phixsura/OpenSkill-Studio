"use client";

interface PlatformStats { commits: number; lines: number; files: number;
  backend_services: number; frontend_components: number; test_files: number; }
interface GrandCapstoneHeroProps { version: string; codename: string; stats: PlatformStats;
  modules: Record<string, string>; techStack: Record<string, string>; achievement: string; }

export function GrandCapstoneHero({ version, codename, stats, modules, techStack, achievement }: GrandCapstoneHeroProps) {
  return (
    <div className="space-y-8">
      <div className="rounded-2xl bg-gradient-to-br from-blue-700 via-purple-700 to-pink-600 p-10 text-center text-white">
        <p className="text-5xl">🏆</p>
        <h1 className="mt-3 text-4xl font-black">OpenSkill Developer Platform</h1>
        <p className="mt-2 text-xl font-medium opacity-80">v{version} — {codename}</p>
        <p className="mt-4 text-lg">{achievement}</p>
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
          <div key={s.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <span className="text-xl">{s.icon}</span>
            <p className="mt-1 text-xl font-bold">{s.value.toLocaleString()}</p>
            <p className="text-[10px] text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <h2 className="text-lg font-bold">Platform Modules</h2>
          <div className="mt-2 grid grid-cols-2 gap-1.5">
            {Object.entries(modules).map(([name, status]) => (
              <div key={name} className="flex items-center gap-1.5 rounded border px-2 py-1 text-xs dark:border-gray-700">
                <span className="text-green-500">●</span>
                <span>{name}</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h2 className="text-lg font-bold">Tech Stack</h2>
          <div className="mt-2 space-y-1">
            {Object.entries(techStack).map(([key, val]) => (
              <div key={key} className="flex justify-between text-sm">
                <span className="capitalize text-gray-400">{key}</span>
                <span className="font-medium">{val}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
