"use client";

interface AppPreviewBannerProps { versionName: string; expiresAt: string; onPublish?: () => void; }

export function AppPreviewBanner({ versionName, expiresAt, onPublish }: AppPreviewBannerProps) {
  return (
    <div className="rounded-lg border border-yellow-300 bg-yellow-50 px-4 py-3 dark:border-yellow-700 dark:bg-yellow-900/20">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">👁️</span>
          <div>
            <p className="text-sm font-semibold text-yellow-800 dark:text-yellow-200">Preview Mode — {versionName}</p>
            <p className="text-xs text-yellow-600 dark:text-yellow-400">Expires {new Date(expiresAt).toLocaleDateString()}</p>
          </div>
        </div>
        {onPublish && (
          <button onClick={onPublish} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-700">
            Publish Now
          </button>
        )}
      </div>
    </div>
  );
}
