"use client";

interface PlatformAboutPageProps { version: string; modules: number; commits: number;
  lines: number; files: number; builder: string; }

export function PlatformAboutPage({ version, modules, commits, lines, files, builder }: PlatformAboutPageProps) {
  return (
    <div className="max-w-2xl mx-auto py-12 text-center space-y-6">
      <div>
        <h1 className="text-3xl font-black mb-2">⚡ OpenSkill Platform</h1>
        <p className="text-sm text-gray-400">v{version} · {modules} modules</p>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border dark:border-gray-700 p-4">
          <p className="text-2xl font-bold">{commits.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Commits</p>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-4">
          <p className="text-2xl font-bold">{lines.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Lines</p>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-4">
          <p className="text-2xl font-bold">{files.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Files</p>
        </div>
      </div>
      <p className="text-sm text-gray-500">Built with {builder}</p>
      <p className="text-lg font-bold text-green-600">✅ FULLY OPERATIONAL</p>
    </div>
  );
}
