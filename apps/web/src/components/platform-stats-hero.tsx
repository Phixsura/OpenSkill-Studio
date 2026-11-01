"use client";

interface PlatformStatsHeroProps { commits: number; lines: number; files: number;
  services: number; components: number; modules: number; }

export function PlatformStatsHero({ commits, lines, files, services, components, modules }: PlatformStatsHeroProps) {
  const stats = [
    { label: "Commits", value: commits.toLocaleString(), icon: "📝" },
    { label: "Lines", value: `${(lines / 1000).toFixed(0)}K`, icon: "📊" },
    { label: "Files", value: files.toLocaleString(), icon: "📁" },
    { label: "Services", value: services.toLocaleString(), icon: "⚙️" },
    { label: "Components", value: components.toLocaleString(), icon: "🧩" },
    { label: "Modules", value: String(modules), icon: "📦" },
  ];
  return (
    <div className="rounded-xl border-2 border-blue-500 overflow-hidden bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10">
      <div className="p-6 text-center">
        <h2 className="text-2xl font-bold text-blue-700 dark:text-blue-400">OpenSkill Developer Platform</h2>
        <p className="text-sm text-gray-400 mt-1">222K+ lines · Fully Operational</p>
      </div>
      <div className="grid grid-cols-6 gap-px bg-blue-200 dark:bg-blue-800">
        {stats.map(s => (
          <div key={s.label} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg">{s.icon}</div>
            <div className="text-lg font-bold text-blue-700 dark:text-blue-400">{s.value}</div>
            <div className="text-[10px] text-gray-400">{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
