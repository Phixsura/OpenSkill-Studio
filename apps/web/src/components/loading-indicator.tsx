"use client";

interface LoadingIndicatorProps { type: string; label?: string; }

export function LoadingIndicator({ type, label }: LoadingIndicatorProps) {
  if (type === "spinner") {
    return (
      <div className="flex items-center gap-2">
        <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        {label && <span className="text-sm text-gray-500">{label}</span>}
      </div>
    );
  }
  if (type === "dots") {
    return (
      <span className="inline-flex gap-1">
        {[0, 1, 2].map(i => (
          <span key={i} className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"
                style={{ animationDelay: `${i * 200}ms` }} />
        ))}
        {label && <span className="text-sm text-gray-500 ml-1">{label}</span>}
      </span>
    );
  }
  if (type === "progress_bar") {
    return (
      <div className="w-full h-1 bg-gray-200 dark:bg-gray-800 overflow-hidden">
        <div className="h-full bg-blue-500 animate-pulse" style={{ width: "60%" }} />
      </div>
    );
  }
  return <div className="animate-pulse bg-gray-200 dark:bg-gray-700 rounded h-8 w-full" />;
}
