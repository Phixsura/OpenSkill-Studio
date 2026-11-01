"use client";

interface ContainerImage { name: string; tag: string; digest: string; sizeMb: number; pushedAt: string; pullCount: number; }
interface ContainerRegistryProps { images: ContainerImage[]; totalSizeMb: number; }

export function ContainerRegistry({ images, totalSizeMb }: ContainerRegistryProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Container Registry</h3>
        <span className="text-xs text-gray-400">{images.length} images · {totalSizeMb}MB</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {images.map((img, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono font-medium">{img.name}</span>
                <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{img.tag}</span>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">{img.sizeMb}MB · {img.pullCount} pulls</p>
            </div>
            <time className="text-xs text-gray-400">{img.pushedAt}</time>
          </div>
        ))}
      </div>
    </div>
  );
}
