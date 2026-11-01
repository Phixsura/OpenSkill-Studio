"use client";

interface Version { version: string; status: string; }
interface VersionStats { total: number; published: number; in_review: number; }
interface VersionManagementLayoutProps { appName: string; currentVersion: string | null; stats: VersionStats;
  onCreateVersion: () => void; children: React.ReactNode; }

export function VersionManagementLayout({ appName, currentVersion, stats, onCreateVersion, children }: VersionManagementLayoutProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">{appName} — Versions</h1>
          <p className="text-sm text-gray-400">
            Current: {currentVersion || "none"} · {stats.total} versions · {stats.published} published
            {stats.in_review > 0 && ` · ${stats.in_review} in review`}
          </p>
        </div>
        <button onClick={onCreateVersion} className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white">
          🆕 New Version
        </button>
      </div>
      <div>{children}</div>
    </div>
  );
}
