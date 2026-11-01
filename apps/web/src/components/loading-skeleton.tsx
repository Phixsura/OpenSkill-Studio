"use client";

interface SkeletonRow { type: string; height?: number; size?: number; lines?: number; count?: number; }
interface LoadingSkeletonProps { layout: string; count: number; }

function SkeletonBlock({ type, height, lines }: SkeletonRow) {
  if (type === "image") return <div className="animate-pulse rounded bg-gray-200 dark:bg-gray-700" style={{ height: height ?? 120 }} />;
  if (type === "avatar") return <div className="animate-pulse rounded-full bg-gray-200 dark:bg-gray-700 h-10 w-10" />;
  if (type === "text") return (
    <div className="space-y-2">{Array.from({ length: lines ?? 1 }).map((_, i) => (
      <div key={i} className="h-3 animate-pulse rounded bg-gray-200 dark:bg-gray-700" style={{ width: `${80 - i * 20}%` }} />
    ))}</div>
  );
  if (type === "badge") return (
    <div className="flex gap-2">{Array.from({ length: 3 }).map((_, i) => (
      <div key={i} className="h-5 w-14 animate-pulse rounded-full bg-gray-200 dark:bg-gray-700" />
    ))}</div>
  );
  return null;
}

export function LoadingSkeleton({ layout, count }: LoadingSkeletonProps) {
  const rows: SkeletonRow[] = layout === "list"
    ? [{ type: "avatar" }, { type: "text", lines: 1 }]
    : [{ type: "image", height: 120 }, { type: "text", lines: 2 }, { type: "badge" }];

  return (
    <div className={layout === "list" ? "space-y-3" : "grid gap-4 sm:grid-cols-2 lg:grid-cols-3"}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-xl border p-4 space-y-3 dark:border-gray-700">
          {rows.map((r, j) => <SkeletonBlock key={j} {...r} />)}
        </div>
      ))}
    </div>
  );
}
