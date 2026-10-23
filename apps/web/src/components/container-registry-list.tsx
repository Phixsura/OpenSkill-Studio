"use client";

interface Image { tag: string; digest: string; size_mb: number; pushed_at: string; }
interface ContainerRegistryListProps { repository: string; images: Image[]; totalSizeMb: number;
  onDelete: (tag: string) => void; onPull: (tag: string) => void; }

export function ContainerRegistryList({ repository, images, totalSizeMb, onDelete, onPull }: ContainerRegistryListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Container Registry</h2>
          <p className="font-mono text-xs text-gray-400">{repository}</p>
        </div>
        <span className="text-xs text-gray-400">{totalSizeMb} MB total</span>
      </div>
      <div className="space-y-1.5">
        {images.map(img => (
          <div key={img.tag} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm font-bold text-blue-600">{img.tag}</span>
                <span className="text-xs text-gray-400">{img.size_mb} MB</span>
              </div>
              <p className="font-mono text-[10px] text-gray-400">{img.digest.slice(0, 19)}...</p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => onPull(img.tag)} className="text-xs text-blue-500">Pull</button>
              {img.tag !== "latest" && (
                <button onClick={() => onDelete(img.tag)} className="text-xs text-red-500">Delete</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
