"use client";

interface Module { status: string; version: string; }
interface PlatformStats { total_commits: number; total_files: number; total_lines: number;
  backend_services: number; frontend_components: number; }
interface PlatformOverviewHeroProps { platformName: string; version: string; status: string;
  modules: Record<string, Module>; stats: PlatformStats; milestones: string[]; }

export function PlatformOverviewHero({ platformName, version, status, modules, stats, milestones }: PlatformOverviewHeroProps) {
  const moduleList = Object.entries(modules);
  return (
    <div className="space-y-6">
      <div className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-center text-white">
        <h1 className="text-3xl font-black">{platformName}</h1>
        <p className="mt-1 text-lg opacity-80">v{version}</p>
        <span className="mt-2 inline-block rounded-full bg-white/20 px-4 py-1 text-sm">
          🟢 {status}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        {[
          { label: "Commits", value: stats.total_commits.toLocaleString() },
          { label: "Files", value: stats.total_files.toLocaleString() },
          { label: "Lines", value: stats.total_lines.toLocaleString() },
          { label: "Services", value: stats.backend_services.toLocaleString() },
          { label: "Components", value: stats.frontend_components.toLocaleString() },
        ].map(s => (
          <div key={s.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <p className="text-xl font-bold">{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div>
        <h2 className="text-lg font-semibold">Platform Modules</h2>
        <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-5">
          {moduleList.map(([key, mod]) => (
            <div key={key} className="rounded border p-2 text-center dark:border-gray-700">
              <span className="text-green-500">●</span>
              <p className="mt-0.5 text-xs font-medium capitalize">{key.replace(/_/g, " ")}</p>
              <p className="text-[10px] text-gray-400">v{mod.version}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
