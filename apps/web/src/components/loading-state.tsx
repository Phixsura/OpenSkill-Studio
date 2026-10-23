"use client";

interface LoadingStateProps { variant: string; message: string | null;
  progressPct: number | null; showProgress: boolean; }

export function LoadingState({ variant, message, progressPct, showProgress }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12" role="status" aria-label={message ?? "Loading"}>
      {variant === "spinner" && (
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
      )}
      {variant === "dots" && (
        <div className="flex gap-1">
          {[0, 1, 2].map(i => (
            <div key={i} className="h-2.5 w-2.5 animate-bounce rounded-full bg-blue-600"
              style={{ animationDelay: `${i * 0.15}s` }} />
          ))}
        </div>
      )}
      {variant === "pulse" && (
        <div className="h-12 w-12 animate-pulse rounded-full bg-blue-200 dark:bg-blue-800" />
      )}
      {showProgress && progressPct !== null && (
        <div className="w-48">
          <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
          </div>
          <p className="mt-1 text-center text-xs text-gray-400">{progressPct}%</p>
        </div>
      )}
      {message && <p className="text-sm text-gray-500">{message}</p>}
    </div>
  );
}
