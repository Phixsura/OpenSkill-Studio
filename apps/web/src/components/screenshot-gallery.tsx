"use client";
import { useState } from "react";

interface Screenshot { screenshotId: string; url: string; caption: string; }

export function ScreenshotGallery({ screenshots, onDelete }: {
  screenshots: Screenshot[]; onDelete?: (id: string) => void;
}) {
  const [selected, setSelected] = useState(0);
  if (!screenshots.length) return <div className="text-center text-gray-400 py-8 text-sm">No screenshots uploaded</div>;

  return (
    <div className="space-y-3">
      <div className="relative rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800 aspect-video flex items-center justify-center">
        <img src={screenshots[selected]?.url} alt={screenshots[selected]?.caption || "Screenshot"}
          className="max-h-full max-w-full object-contain" />
        {screenshots[selected]?.caption && (
          <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-2">{screenshots[selected].caption}</div>
        )}
      </div>
      <div className="flex gap-2 overflow-x-auto">
        {screenshots.map((ss, i) => (
          <button key={ss.screenshotId} onClick={() => setSelected(i)}
            className={`shrink-0 w-16 h-10 rounded-lg overflow-hidden border-2 ${i === selected ? "border-blue-500" : "border-transparent"}`}>
            <img src={ss.url} alt="" className="w-full h-full object-cover" />
          </button>
        ))}
      </div>
      {onDelete && (
        <button onClick={() => onDelete(screenshots[selected]?.screenshotId)}
          className="text-xs text-red-400 hover:text-red-600">🗑️ Delete selected</button>
      )}
    </div>
  );
}
