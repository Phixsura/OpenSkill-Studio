"use client";
interface ImageInfo { name: string; tags: string[]; totalSizeMb: number; }
interface ImageRegistryPanelProps { images: ImageInfo[]; totalImages: number; totalTags: number; totalSizeMb: number; }
export function ImageRegistryPanel({ images, totalImages, totalTags, totalSizeMb }: ImageRegistryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐳 Image Registry</h3>
        <span className="text-xs text-gray-400">{totalImages} images · {totalTags} tags · {totalSizeMb}MB</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {images.map(img => (
          <div key={img.name} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono font-semibold">{img.name}</span>
              <span className="text-gray-400">{img.totalSizeMb}MB</span>
            </div>
            <div className="flex gap-1">
              {img.tags.map(t => (
                <span key={t} className="px-1 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-[10px]">{t}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
