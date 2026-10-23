"use client";

interface SkeletonBlock { type: string; w?: string; h?: string;
  rows?: number; cols?: number; fields?: number;
  items?: { w: string; h: string }[]; }
interface SkeletonLoaderProps { blocks: SkeletonBlock[]; }

export function SkeletonLoader({ blocks }: SkeletonLoaderProps) {
  return (
    <div className="space-y-4 animate-pulse">
      {blocks.map((b, i) => {
        if (b.type === "header") return (
          <div key={i} className="bg-gray-200 dark:bg-gray-700 rounded" style={{ width: b.w, height: b.h }} />
        );
        if (b.type === "row") return (
          <div key={i} className="flex gap-3">
            {(b.items || []).map((item, j) => (
              <div key={j} className="bg-gray-200 dark:bg-gray-700 rounded" style={{ width: item.w, height: item.h }} />
            ))}
          </div>
        );
        if (b.type === "chart") return (
          <div key={i} className="bg-gray-200 dark:bg-gray-700 rounded-xl" style={{ width: b.w, height: b.h }} />
        );
        if (b.type === "table") return (
          <div key={i} className="space-y-2">
            {Array.from({ length: b.rows || 3 }, (_, r) => (
              <div key={r} className="flex gap-2">
                {Array.from({ length: b.cols || 3 }, (_, c) => (
                  <div key={c} className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded" />
                ))}
              </div>
            ))}
          </div>
        );
        if (b.type === "form") return (
          <div key={i} className="space-y-3">
            {Array.from({ length: b.fields || 3 }, (_, f) => (
              <div key={f} className="bg-gray-200 dark:bg-gray-700 rounded" style={{ height: b.h || "40px" }} />
            ))}
          </div>
        );
        return null;
      })}
    </div>
  );
}
