"use client";

import { useState } from "react";

interface Screenshot { url: string; altText: string; order: number; }
interface ScreenshotGalleryProps { screenshots: Screenshot[]; meetsMinimum: boolean; }

export function ScreenshotGallery({ screenshots, meetsMinimum }: ScreenshotGalleryProps) {
  const [active, setActive] = useState(0);
  if (screenshots.length === 0) {
    return <p className="py-8 text-center text-sm text-gray-400">No screenshots uploaded</p>;
  }
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Screenshots</h3>
        {!meetsMinimum && <span className="text-xs text-yellow-600">⚠ Minimum 2 required</span>}
      </div>
      <div className="aspect-video overflow-hidden rounded-lg border dark:border-gray-700 bg-gray-100 dark:bg-gray-800">
        <img src={screenshots[active]?.url} alt={screenshots[active]?.altText}
          className="h-full w-full object-contain" />
      </div>
      <div className="flex gap-2 overflow-x-auto">
        {screenshots.map((s, i) => (
          <button key={i} onClick={() => setActive(i)}
            className={`h-16 w-24 shrink-0 overflow-hidden rounded border ${active === i ? "ring-2 ring-blue-500" : "dark:border-gray-700"}`}>
            <img src={s.url} alt={s.altText} className="h-full w-full object-cover" />
          </button>
        ))}
      </div>
    </div>
  );
}
