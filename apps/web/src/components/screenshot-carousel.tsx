"use client";
import { useState } from "react";

interface Screenshot { url: string; alt: string; caption: string; }
interface ScreenshotCarouselProps { screenshots: Screenshot[]; appName: string; }

export function ScreenshotCarousel({ screenshots, appName }: ScreenshotCarouselProps) {
  const [current, setCurrent] = useState(0);
  if (!screenshots.length) return <p className="text-sm text-gray-400">No screenshots</p>;
  const s = screenshots[current];
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-100 dark:bg-gray-800 flex items-center justify-center min-h-[200px] p-4">
        <img src={s.url} alt={s.alt} className="max-h-64 rounded-lg shadow" />
      </div>
      <div className="p-3 flex items-center justify-between">
        <div>
          {s.caption && <p className="text-xs text-gray-500">{s.caption}</p>}
          <p className="text-xs text-gray-400">{current + 1} / {screenshots.length}</p>
        </div>
        <div className="flex gap-1">
          <button onClick={() => setCurrent(Math.max(0, current - 1))} disabled={current === 0}
            className="px-2 py-1 text-xs rounded border disabled:opacity-30">←</button>
          <button onClick={() => setCurrent(Math.min(screenshots.length - 1, current + 1))}
            disabled={current === screenshots.length - 1}
            className="px-2 py-1 text-xs rounded border disabled:opacity-30">→</button>
        </div>
      </div>
    </div>
  );
}
