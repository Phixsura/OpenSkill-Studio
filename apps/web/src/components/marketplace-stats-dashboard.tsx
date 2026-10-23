"use client";

interface CodebaseStats { commits: number; lines: number; files: number; }
interface MarketplaceMetrics { totalApps: number; totalDevelopers: number; totalDownloads: number; avgRating: number; }
interface InfraStats { uptimePct: number; avgResponseMs: number; regions: number; }
interface MarketplaceStatsDashboardProps { codebase: CodebaseStats; marketplace: MarketplaceMetrics;
  infra: InfraStats; modules: string[]; achievement: string; }

export function MarketplaceStatsDashboard({ codebase, marketplace, infra, modules, achievement }: MarketplaceStatsDashboardProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white text-center">
        <h1 className="text-2xl font-extrabold">OpenSkill Developer Platform</h1>
        <p className="mt-2 text-sm opacity-90">{achievement}</p>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{codebase.commits.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Commits</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{(codebase.lines / 1000).toFixed(0)}K</p>
          <p className="text-xs text-gray-400">Lines</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{codebase.files.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Files</p>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{marketplace.totalApps.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Apps</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{marketplace.totalDevelopers.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Developers</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{(marketplace.totalDownloads / 1_000_000).toFixed(1)}M</p>
          <p className="text-xs text-gray-400">Downloads</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{infra.uptimePct}%</p>
          <p className="text-xs text-gray-400">Uptime</p>
        </div>
      </div>
      <div>
        <h3 className="text-sm font-semibold mb-2">Platform Modules ({modules.length})</h3>
        <div className="flex flex-wrap gap-1.5">
          {modules.map(m => (
            <span key={m} className="rounded-full border px-3 py-1 text-xs dark:border-gray-700">✅ {m}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
