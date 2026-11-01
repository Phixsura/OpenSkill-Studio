"use client";

interface Codebase { commits: number; lines: number; files: number;
  backendServices: number; frontendComponents: number; }
interface UltimatePlatformSummaryProps { platform: string; version: string;
  status: string; codebase: Codebase; pagesBuilt: string[];
  integrations: string[]; }

export function UltimatePlatformSummary({ platform, version, status, codebase,
  pagesBuilt, integrations }: UltimatePlatformSummaryProps) {
  return (
    <div className="mx-auto max-w-4xl space-y-8 py-8">
      <div className="rounded-2xl bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500 p-10 text-center text-white">
        <h1 className="text-4xl font-extrabold">{platform}</h1>
        <p className="mt-2 text-lg">{version} · {status}</p>
      </div>
      <div className="grid grid-cols-5 gap-3">
        {Object.entries({Commits: codebase.commits, Lines: codebase.lines, Files: codebase.files,
          Backend: codebase.backendServices, Frontend: codebase.frontendComponents}).map(([k, v]) => (
          <div key={k} className="rounded-xl border p-3 text-center dark:border-gray-700">
            <p className="text-lg font-bold">{v.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{k}</p>
          </div>
        ))}
      </div>
      <div>
        <h2 className="text-lg font-bold mb-3">📄 {pagesBuilt.length} Pages Built</h2>
        <div className="flex flex-wrap gap-1.5">
          {pagesBuilt.map(p => <span key={p} className="rounded-full bg-green-100 px-2.5 py-0.5 text-xs text-green-700 dark:bg-green-900/30 dark:text-green-400">✅ {p}</span>)}
        </div>
      </div>
      <div>
        <h2 className="text-lg font-bold mb-3">🔌 {integrations.length} Integrations</h2>
        <div className="flex flex-wrap gap-2">
          {integrations.map(i => <span key={i} className="rounded-lg border px-3 py-1 text-sm dark:border-gray-700">{i}</span>)}
        </div>
      </div>
    </div>
  );
}
