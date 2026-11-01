"use client";

interface Version { version: string; reviewStatus: string; createdAt: string; }

interface AppVersionListProps { versions: Version[]; }

export function AppVersionList({ versions }: AppVersionListProps) {
  if (versions.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No versions</p>;

  return (
    <ul className="space-y-2">
      {versions.map(v => (
        <li key={v.version} className="flex items-center justify-between rounded border border-gray-200 p-3 dark:border-gray-700">
          <span className="font-mono font-semibold">{v.version}</span>
          <div className="flex items-center gap-2">
            <span className={`rounded-full px-2 py-0.5 text-xs ${
              v.reviewStatus === "approved" ? "bg-green-100 text-green-800" :
              v.reviewStatus === "rejected" ? "bg-red-100 text-red-800" :
              "bg-yellow-100 text-yellow-800"
            }`}>{v.reviewStatus}</span>
            <span className="text-xs text-gray-400">{v.createdAt}</span>
          </div>
        </li>
      ))}
    </ul>
  );
}
