"use client";
interface GrandTotalPanelProps { commits: number; lines: number; files: number;
  services: number; components: number; tests: number; modules: number;
  securityFixes: number; status: string; }
export function GrandTotalPanel({ commits, lines, files, services, components,
  tests, modules, securityFixes, status }: GrandTotalPanelProps) {
  return (
    <div className="rounded-2xl border-2 border-yellow-500 bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50 dark:from-yellow-950 dark:via-amber-950 dark:to-orange-950 overflow-hidden">
      <div className="p-6 text-center">
        <div className="text-3xl mb-1">🏆</div>
        <h1 className="text-2xl font-black">OpenSkill Developer Platform</h1>
        <p className="text-sm text-amber-700 dark:text-amber-400">{status} · {modules} Modules</p>
      </div>
      <div className="grid grid-cols-4 gap-2 px-6 pb-4 text-center text-xs">
        {[
          { label: "Commits", value: commits.toLocaleString(), icon: "📦" },
          { label: "Lines", value: `${(lines / 1000).toFixed(0)}K`, icon: "📝" },
          { label: "Files", value: files.toLocaleString(), icon: "📁" },
          { label: "Services", value: services.toLocaleString(), icon: "⚙️" },
          { label: "Components", value: components.toLocaleString(), icon: "🧩" },
          { label: "Tests", value: tests.toLocaleString(), icon: "✅" },
          { label: "Modules", value: modules.toString(), icon: "📦" },
          { label: "Security", value: `${securityFixes} fixes`, icon: "🔒" },
        ].map(s => (
          <div key={s.label} className="bg-white/50 dark:bg-black/20 rounded-lg p-2">
            <div className="text-lg">{s.icon}</div>
            <div className="font-bold text-amber-700 dark:text-amber-400">{s.value}</div>
            <div className="text-[10px] text-gray-500">{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
