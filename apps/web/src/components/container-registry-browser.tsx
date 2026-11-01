"use client";

interface ContainerImage { name: string; tag: string; digest: string; sizeMb: number; layers: number; }
interface ContainerRegistryBrowserProps { images: ContainerImage[]; totalImages: number;
  totalSizeMb: number; repositories: number; onDelete: (name: string, tag: string) => void; }

export function ContainerRegistryBrowser({ images, totalImages, totalSizeMb, repositories, onDelete }: ContainerRegistryBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Container Registry</h3>
        <span className="text-xs text-gray-400">{totalImages} images · {totalSizeMb} MB · {repositories} repos</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {images.map(img => (
          <div key={`${img.name}:${img.tag}`} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-sm"><span className="font-mono font-medium">{img.name}</span>:<span className="text-blue-500">{img.tag}</span></div>
              <div className="text-[10px] text-gray-400">{img.digest} · {img.layers} layers · {img.sizeMb} MB</div>
            </div>
            <button onClick={() => onDelete(img.name, img.tag)} className="text-xs text-red-500 hover:underline">Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}
