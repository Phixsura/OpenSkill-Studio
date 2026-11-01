"use client";

interface Module { name: string; status: string; services: number; }
interface PlatformStats { commits: number; lines: number; files: number; services: number; components: number; tests: number; }
interface PlatformOverviewPageProps { platform: string; version: string; status: string;
  modules: Module[]; stats: PlatformStats; achievement: string; }

export function PlatformOverviewPage({ platform, version, status, modules, stats, achievement }: PlatformOverviewPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="text-center py-8">
        <h1 className="text-3xl font-extrabold">{platform}</h1>
        <p className="mt-2 text-sm text-gray-400">v{version} · {status}</p>
        <p className="mt-4 text-lg font-bold text-blue-600">{achievement}</p>
      </div>
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {Object.entries(stats).map(([k, v]) => (
          <div key={k} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <p className="text-lg font-bold">{typeof v === "number" ? v.toLocaleString() : v}</p>
            <p className="text-xs text-gray-400 capitalize">{k}</p>
          </div>
        ))}
      </div>
      <div>
        <h2 className="text-sm font-semibold mb-3">Platform Modules</h2>
        <div className="grid gap-2 sm:grid-cols-2">
          {modules.map(m => (
            <div key={m.name} className="flex items-center justify-between rounded-lg border px-4 py-2.5 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <span>{m.status}</span>
                <span className="text-sm font-medium">{m.name}</span>
              </div>
              <span className="text-xs text-gray-400">{m.services} services</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
