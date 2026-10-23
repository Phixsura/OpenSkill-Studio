"use client";

interface SchemaVersion { version: string; hash: string; typeCount: number; sdlLength: number; }
interface GqlSchemaViewerProps { name: string; versions: SchemaVersion[];
  latestVersion: string | null; totalVersions: number; }

export function GqlSchemaViewer({ name, versions, latestVersion, totalVersions }: GqlSchemaViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📐 {name} Schema</h3>
        <span className="text-xs text-gray-400">{totalVersions} versions · latest: {latestVersion ?? "none"}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {versions.map(v => (
          <div key={v.version} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className="text-sm font-mono font-medium">v{v.version}</span>
              {v.version === latestVersion && <span className="text-[10px] text-blue-500">★</span>}
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{v.typeCount} types</span>
              <span>{v.sdlLength} chars</span>
              <span className="font-mono">{v.hash}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
