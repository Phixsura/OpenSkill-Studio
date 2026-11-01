"use client";

import { useState } from "react";

interface Screenshot { index: number; url: string; alt: string; thumbnail_url: string; }
interface ScreenshotGalleryViewerProps { screenshots: Screenshot[]; }

export function ScreenshotGalleryViewer({ screenshots }: ScreenshotGalleryViewerProps) {
  const [selected, setSelected] = useState(0);
  if (screenshots.length === 0) return <p className="text-sm text-gray-400">No screenshots available</p>;

  return (
    <div className="space-y-3">
      <div className="overflow-hidden rounded-lg border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800">
        <div className="aspect-video flex items-center justify-center">
          <p className="text-sm text-gray-400">{screenshots[selected]?.alt}</p>
        </div>
      </div>
      {screenshots.length > 1 && (
        <div className="flex gap-2 overflow-x-auto">
          {screenshots.map((s, i) => (
            <button key={i} onClick={() => setSelected(i)}
              className={`flex-shrink-0 rounded border p-1 ${selected === i ? "border-blue-500 ring-2 ring-blue-200" : "border-gray-200 dark:border-gray-700"}`}>
              <div className="h-12 w-20 rounded bg-gray-100 dark:bg-gray-700" />
            </button>
          ))}
        </div>
      )}
      <p className="text-center text-xs text-gray-400">{selected + 1} / {screenshots.length}</p>
    </div>
  );
}
