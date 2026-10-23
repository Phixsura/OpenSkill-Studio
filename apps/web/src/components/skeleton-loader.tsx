"use client";

interface SkeletonLoaderProps { count?: number; height?: string; className?: string; }

export function SkeletonLoader({ count = 3, height = "h-20", className = "" }: SkeletonLoaderProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className={`animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700 ${height}`}>
          <div className="flex h-full items-center gap-3 p-4">
            <div className="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600" />
            <div className="flex-1 space-y-2">
              <div className="h-3 w-3/4 rounded bg-gray-300 dark:bg-gray-600" />
              <div className="h-2 w-1/2 rounded bg-gray-300 dark:bg-gray-600" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
