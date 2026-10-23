"use client";

interface PlatformStatsHeroProps { commits: number; lines: number; files: number;
  services: number; components: number; tests: number; version: string; }

export function PlatformStatsHero({ commits, lines, files, services, components, tests, version }: PlatformStatsHeroProps) {
  const stats = [
    { label: "Commits", value: commits, icon: "📝" },
    { label: "Lines", value: lines, icon: "📏" },
    { label: "Files", value: files, icon: "📁" },
    { label: "Services", value: services, icon: "⚙️" },
    { label: "Components", value: components, icon: "🧩" },
    { label: "Tests", value: tests, icon: "🧪" },
  ];
  return (
    <div className="space-y-6">
      <div className="rounded-xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-8 text-center text-white">
        <p className="text-4xl">🏆</p>
        <h1 className="mt-2 text-3xl font-black">OpenSkill Developer Platform</h1>
        <p className="mt-1 text-lg opacity-80">v{version} — Fully Operational</p>
      </div>
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {stats.map(s => (
          <div key={s.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <span className="text-xl">{s.icon}</span>
            <p className="mt-1 text-xl font-bold">{s.value.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
