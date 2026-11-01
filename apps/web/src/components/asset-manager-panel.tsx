"use client";

interface Asset { path: string; size: number; content_type: string; hash: string; }
interface AssetManagerPanelProps { assets: Asset[]; totalSize: number; version: string; onInvalidate: (path: string) => void; }

export function AssetManagerPanel({ assets, totalSize, version, onInvalidate }: AssetManagerPanelProps) {
  const formatSize = (b: number) => b < 1024 ? `${b}B` : b < 1048576 ? `${(b / 1024).toFixed(1)}KB` : `${(b / 1048576).toFixed(1)}MB`;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Assets</h3>
        <span className="text-xs text-gray-400">v{version} · {formatSize(totalSize)}</span>
      </div>
      <ul className="mt-3 space-y-1">
        {assets.map(a => (
          <li key={a.path} className="flex items-center justify-between text-xs">
            <span className="font-mono truncate max-w-[200px]">{a.path}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">{formatSize(a.size)}</span>
              <button onClick={() => onInvalidate(a.path)} className="text-blue-600">🔄</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
