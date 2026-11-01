"use client";

interface RecommendedExtension {
  id: string;
  name: string;
  icon: string;
  description: string;
  rating: number;
  downloads: number;
  matchScore: number;
  reason: string;
}

export function ExtensionRecommendationList({
  recommendations,
  title,
  onInstall,
  onDismiss,
}: {
  recommendations: RecommendedExtension[];
  title?: string;
  onInstall?: (id: string) => void;
  onDismiss?: (id: string) => void;
}) {
  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-bold">{title || "💡 Recommended for You"}</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {recommendations.map((ext) => (
          <div key={ext.id} className="rounded-xl border dark:border-gray-700 p-4 flex gap-3">
            <span className="text-3xl shrink-0">{ext.icon}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm truncate">{ext.name}</span>
                <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 px-1.5 py-0.5 rounded-full">
                  {ext.matchScore}% match
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{ext.description}</p>
              <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                <span>★ {ext.rating.toFixed(1)}</span>
                <span>⬇ {ext.downloads.toLocaleString()}</span>
                <span className="text-blue-400">{ext.reason}</span>
              </div>
              <div className="flex gap-2 mt-2">
                <button onClick={() => onInstall?.(ext.id)}
                  className="text-xs bg-blue-600 text-white px-3 py-1 rounded-lg">
                  Install
                </button>
                <button onClick={() => onDismiss?.(ext.id)}
                  className="text-xs text-gray-400 hover:text-gray-600">
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
