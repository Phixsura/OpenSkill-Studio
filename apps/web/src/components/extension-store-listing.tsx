"use client";

interface ExtensionListing {
  id: string;
  name: string;
  icon: string;
  author: string;
  version: string;
  description: string;
  longDescription: string;
  category: string;
  downloads: number;
  rating: number;
  reviewCount: number;
  screenshots: string[];
  tags: string[];
  lastUpdated: string;
  installed: boolean;
}

export function ExtensionStoreListing({
  extension,
  onInstall,
  onUninstall,
}: {
  extension: ExtensionListing;
  onInstall?: () => void;
  onUninstall?: () => void;
}) {
  const stars = Math.round(extension.rating);

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="text-5xl">{extension.icon}</div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{extension.name}</h1>
          <p className="text-sm text-gray-500">
            by {extension.author} · v{extension.version} · Updated {extension.lastUpdated}
          </p>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-yellow-500">{"★".repeat(stars)}{"☆".repeat(5 - stars)}</span>
            <span className="text-sm text-gray-500">{extension.rating.toFixed(1)} ({extension.reviewCount} reviews)</span>
            <span className="text-sm text-gray-500">⬇ {extension.downloads.toLocaleString()}</span>
          </div>
        </div>
        <button
          onClick={() => extension.installed ? onUninstall?.() : onInstall?.()}
          className={`shrink-0 rounded-lg px-6 py-2.5 text-sm font-semibold ${
            extension.installed
              ? "border dark:border-gray-600 text-red-600"
              : "bg-blue-600 text-white hover:bg-blue-700"
          }`}
        >
          {extension.installed ? "Uninstall" : "Install"}
        </button>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2">
        <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2.5 py-1 rounded-full">
          {extension.category}
        </span>
        {extension.tags.map((tag) => (
          <span key={tag} className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 px-2.5 py-1 rounded-full">
            {tag}
          </span>
        ))}
      </div>

      {/* Description */}
      <div>
        <h2 className="font-semibold mb-2">About</h2>
        <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
          {extension.longDescription}
        </p>
      </div>

      {/* Screenshots */}
      {extension.screenshots.length > 0 && (
        <div>
          <h2 className="font-semibold mb-2">Screenshots</h2>
          <div className="flex gap-3 overflow-x-auto">
            {extension.screenshots.map((src, i) => (
              <div key={i} className="shrink-0 w-64 h-40 rounded-lg bg-gray-200 dark:bg-gray-800 flex items-center justify-center text-gray-400">
                📸 {src}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
