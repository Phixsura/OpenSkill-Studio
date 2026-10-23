"use client";

interface SkeletonRow { type: string; width?: string; height?: number; size?: number; }
interface LoadingSkeletonProps { rows: SkeletonRow[]; count?: number; animated?: boolean; }

export function LoadingSkeleton({ rows, count = 1, animated = true }: LoadingSkeletonProps) {
  const animClass = animated ? "animate-pulse" : "";
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, ci) => (
        <div key={ci} className={`space-y-3 ${animClass}`}>
          {rows.map((row, ri) => {
            if (row.type === "circle") {
              return (
                <div key={ri} className="rounded-full bg-gray-200 dark:bg-gray-700"
                  style={{ width: row.size ?? 40, height: row.size ?? 40 }} />
              );
            }
            if (row.type === "rect") {
              return (
                <div key={ri} className="rounded-lg bg-gray-200 dark:bg-gray-700"
                  style={{ width: row.width ?? "100%", height: row.height ?? 40 }} />
              );
            }
            return (
              <div key={ri} className="rounded bg-gray-200 dark:bg-gray-700"
                style={{ width: row.width ?? "100%", height: row.height ?? 14 }} />
            );
          })}
        </div>
      ))}
    </div>
  );
}
