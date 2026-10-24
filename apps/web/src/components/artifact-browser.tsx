"use client";

interface Artifact { name: string; version: string; sizeMb: number; digest: string; downloads: number; }
interface ArtifactBrowserProps { artifacts: Artifact[]; totalSizeMb: number;
  totalDownloads: number; }

export function ArtifactBrowser({ artifacts, totalSizeMb, totalDownloads }: ArtifactBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Build Artifacts</h3>
        <span className="text-xs text-gray-400">{artifacts.length} artifacts · {totalSizeMb} MB · {totalDownloads} downloads</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {artifacts.map(a => (
          <div key={`${a.name}:${a.version}`} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-sm"><span className="font-mono font-medium">{a.name}</span>:<span className="text-blue-500">{a.version}</span></div>
              <div className="text-[10px] text-gray-400 font-mono">{a.digest} · {a.sizeMb} MB</div>
            </div>
            <span className="text-xs text-gray-400">{a.downloads} downloads</span>
          </div>
        ))}
      </div>
    </div>
  );
}
