"use client";

interface StorageObj { key: string; sizeBytes: number; contentType: string; uploadedAt: number; isPublic: boolean; }
interface StorageUsage { objectCount: number; totalBytes: number; }

function formatSize(b: number) {
  if (b < 1024) return `${b} B`;
  if (b < 1048576) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / 1048576).toFixed(1)} MB`;
}

export function StorageBrowser({ objects, usage, onDelete }: {
  objects: StorageObj[]; usage: StorageUsage; onDelete?: (key: string) => void;
}) {
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-sm">Storage ({usage.objectCount} objects)</h3>
        <span className="text-xs text-gray-500">{formatSize(usage.totalBytes)} used</span>
      </div>
      {objects.length === 0 ? (
        <div className="text-center text-gray-400 py-6 text-sm">No files uploaded</div>
      ) : (
        <div className="space-y-1">
          {objects.map(o => (
            <div key={o.key} className="flex items-center justify-between border dark:border-gray-700 rounded-lg p-2 text-xs">
              <div className="flex items-center gap-2 min-w-0">
                <span className="font-mono truncate">{o.key}</span>
                {o.isPublic && <span className="bg-green-100 text-green-600 px-1 rounded text-[10px]">public</span>}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="text-gray-400">{formatSize(o.sizeBytes)}</span>
                <button onClick={() => onDelete?.(o.key)} className="text-red-400 hover:text-red-600">🗑</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
