"use client";

interface FileEntry { path: string; size: number; }
interface FilesystemBrowserProps { files: FileEntry[]; usedBytes: number; quotaBytes: number; onDelete: (path: string) => void; }

export function FilesystemBrowser({ files, usedBytes, quotaBytes, onDelete }: FilesystemBrowserProps) {
  const usagePct = Math.round((usedBytes / Math.max(quotaBytes, 1)) * 100);
  const formatSize = (b: number) => b < 1024 ? `${b}B` : b < 1048576 ? `${(b / 1024).toFixed(1)}KB` : `${(b / 1048576).toFixed(1)}MB`;

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Sandbox Files</h3>
        <span className="text-xs text-gray-400">{formatSize(usedBytes)} / {formatSize(quotaBytes)} ({usagePct}%)</span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${usagePct > 80 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${usagePct}%` }} />
      </div>
      {files.length === 0 ? <p className="mt-3 text-sm text-gray-400">No files.</p> : (
        <ul className="mt-3 space-y-1">
          {files.map(f => (
            <li key={f.path} className="flex items-center justify-between text-sm">
              <span className="font-mono text-xs">{f.path}</span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">{formatSize(f.size)}</span>
                <button onClick={() => onDelete(f.path)} className="text-xs text-red-500">🗑️</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
