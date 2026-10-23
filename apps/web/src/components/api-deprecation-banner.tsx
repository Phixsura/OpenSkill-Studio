"use client";

interface ApiDeprecationBannerProps { path: string; method: string; sunsetDate: string; replacement?: string; }

export function ApiDeprecationBanner({ path, method, sunsetDate, replacement }: ApiDeprecationBannerProps) {
  return (
    <div className="rounded-lg border border-yellow-300 bg-yellow-50 p-4 dark:border-yellow-700 dark:bg-yellow-900/20">
      <div className="flex items-center gap-2">
        <span className="text-lg">⚠️</span>
        <div>
          <p className="text-sm font-semibold text-yellow-800 dark:text-yellow-200">
            {method} <code>{path}</code> is deprecated
          </p>
          <p className="text-xs text-yellow-700 dark:text-yellow-300">Sunset: {sunsetDate}</p>
          {replacement && (
            <p className="mt-1 text-xs text-yellow-600 dark:text-yellow-400">
              ➡️ Use <code className="font-semibold">{replacement}</code> instead
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
