"use client";

interface Screenshot { url: string; filename: string; dimensions: string; }
interface ScreenshotUploadGridProps { screenshots: Screenshot[];
  maxCount: number; onUpload: () => void; onRemove: (idx: number) => void; }

export function ScreenshotUploadGrid({ screenshots, maxCount, onUpload, onRemove }: ScreenshotUploadGridProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🖼️ Screenshots</h3>
        <span className="text-xs text-gray-400">{screenshots.length}/{maxCount}</span>
      </div>
      <div className="grid grid-cols-4 gap-2">
        {screenshots.map((s, i) => (
          <div key={i} className="relative rounded-lg overflow-hidden border dark:border-gray-700">
            <img src={s.url} alt={s.filename} className="w-full h-24 object-cover" />
            <button onClick={() => onRemove(i)}
              className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center">×</button>
            <p className="text-[10px] text-gray-400 text-center py-0.5">{s.dimensions}</p>
          </div>
        ))}
        {screenshots.length < maxCount && (
          <button onClick={onUpload}
            className="h-24 rounded-lg border-2 border-dashed dark:border-gray-600 flex items-center justify-center text-gray-400 hover:text-gray-600">
            <span className="text-2xl">+</span>
          </button>
        )}
      </div>
    </div>
  );
}
