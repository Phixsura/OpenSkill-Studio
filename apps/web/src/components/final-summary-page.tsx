"use client";

interface Codebase { commits: number; lines: number; files: number; }
interface FinalSummaryPageProps { platform: string; version: string; status: string;
  achievement: string; codebase: Codebase; modules: Record<string, string>;
  milestones: string[]; }

export function FinalSummaryPage({ platform, version, status, achievement, codebase, modules, milestones }: FinalSummaryPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-8 py-8">
      <div className="rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-8 text-center text-white">
        <h1 className="text-3xl font-extrabold">{platform}</h1>
        <p className="mt-2 text-lg opacity-90">v{version} · {status}</p>
        <p className="mt-4 text-xl font-bold">{achievement}</p>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-3xl font-bold">{codebase.commits.toLocaleString()}</p>
          <p className="text-sm text-gray-400">Commits</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-3xl font-bold">{(codebase.lines / 1000).toFixed(0)}K</p>
          <p className="text-sm text-gray-400">Lines</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-3xl font-bold">{codebase.files.toLocaleString()}</p>
          <p className="text-sm text-gray-400">Files</p>
        </div>
      </div>
      <div>
        <h2 className="text-lg font-bold mb-3">Platform Modules ({Object.keys(modules).length})</h2>
        <div className="grid gap-2 sm:grid-cols-2">
          {Object.entries(modules).map(([name, status]) => (
            <div key={name} className="flex items-center justify-between rounded-lg border px-4 py-2 dark:border-gray-700">
              <span className="text-sm font-medium">{name}</span>
              <span className="text-xs">{status}</span>
            </div>
          ))}
        </div>
      </div>
      <div>
        <h2 className="text-lg font-bold mb-3">Milestones ({milestones.length})</h2>
        <div className="flex flex-wrap gap-1.5">
          {milestones.map(m => (
            <span key={m} className="rounded-full bg-green-100 px-3 py-1 text-xs text-green-700 dark:bg-green-900/30 dark:text-green-400">🏆 {m}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
