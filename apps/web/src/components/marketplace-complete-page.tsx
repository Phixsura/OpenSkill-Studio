"use client";

interface Module { status: string; services: number; }
interface Codebase { commits: number; lines: number; files: number;
  backendServices: number; frontendComponents: number; testFiles: number; }
interface MarketplaceCompletePageProps { platform: string; version: string; status: string;
  achievement: string; codebase: Codebase; modules: Record<string, Module>; milestones: string[]; }

export function MarketplaceCompletePage({ platform, version, status, achievement, codebase, modules, milestones }: MarketplaceCompletePageProps) {
  return (
    <div className="mx-auto max-w-4xl space-y-8 py-8">
      <div className="rounded-2xl bg-gradient-to-r from-yellow-500 via-red-500 to-purple-600 p-10 text-center text-white">
        <h1 className="text-4xl font-extrabold">{platform}</h1>
        <p className="mt-2 text-lg opacity-90">v{version} · {status}</p>
        <p className="mt-4 text-2xl font-bold">{achievement}</p>
      </div>
      <div className="grid grid-cols-3 gap-4 sm:grid-cols-6">
        {[
          { label: "Commits", value: codebase.commits },
          { label: "Lines", value: codebase.lines },
          { label: "Files", value: codebase.files },
          { label: "Services", value: codebase.backendServices },
          { label: "Components", value: codebase.frontendComponents },
          { label: "Tests", value: codebase.testFiles },
        ].map(s => (
          <div key={s.label} className="rounded-xl border p-3 text-center dark:border-gray-700">
            <p className="text-lg font-bold">{s.value.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div>
        <h2 className="text-lg font-bold mb-3">Platform Modules ({Object.keys(modules).length})</h2>
        <div className="grid gap-2 sm:grid-cols-2">
          {Object.entries(modules).map(([name, mod]) => (
            <div key={name} className="flex items-center justify-between rounded-lg border px-4 py-2 dark:border-gray-700">
              <span className="text-sm capitalize">{name.replace(/_/g, " ")}</span>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-400">{mod.services} svc</span>
                <span className="text-green-600">✅</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div>
        <h2 className="text-lg font-bold mb-3">🏆 Milestones ({milestones.length})</h2>
        <div className="flex flex-wrap gap-1.5">
          {milestones.map(m => (
            <span key={m} className="rounded-full bg-gradient-to-r from-yellow-100 to-orange-100 px-3 py-1 text-xs font-medium text-orange-700 dark:from-yellow-900/30 dark:to-orange-900/30 dark:text-orange-400">
              🏆 {m}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
