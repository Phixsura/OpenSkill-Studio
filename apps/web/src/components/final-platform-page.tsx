"use client";

interface Stats { commits: number; lines: number; files: number; }
interface FinalPlatformPageProps { platform: string; version: string; status: string;
  stats: Stats; modules: number; highlights: string[]; achievement: string; }

export function FinalPlatformPage({ platform, version, status, stats, modules, highlights, achievement }: FinalPlatformPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-8 py-8">
      <div className="rounded-2xl bg-gradient-to-r from-yellow-500 via-red-500 to-purple-600 p-10 text-center text-white">
        <h1 className="text-4xl font-extrabold">{platform}</h1>
        <p className="mt-2 text-lg opacity-90">v{version} · {status}</p>
        <p className="mt-4 text-2xl font-bold">{achievement}</p>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-3xl font-bold">{stats.commits.toLocaleString()}</p>
          <p className="text-sm text-gray-400">Commits</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-3xl font-bold">{(stats.lines / 1000).toFixed(0)}K</p>
          <p className="text-sm text-gray-400">Lines</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-3xl font-bold">{stats.files.toLocaleString()}</p>
          <p className="text-sm text-gray-400">Files</p>
        </div>
      </div>
      <div className="text-center">
        <p className="text-lg font-bold">{modules} Platform Modules — ALL ✅ OPERATIONAL</p>
      </div>
      <div>
        <h2 className="text-lg font-bold mb-3">🏆 Platform Highlights</h2>
        <ul className="space-y-2">
          {highlights.map((h, i) => (
            <li key={i} className="flex items-start gap-2 text-sm">
              <span className="text-green-500 mt-0.5">✅</span>{h}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
