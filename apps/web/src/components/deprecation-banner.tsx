"use client";

interface DeprecationBannerProps {
  version: string;
  sunsetDate: string;
  daysRemaining: number;
  replacementVersion?: string;
  migrationGuideUrl?: string;
}

export function DeprecationBanner({ version, sunsetDate, daysRemaining, replacementVersion, migrationGuideUrl }: DeprecationBannerProps) {
  const urgent = daysRemaining <= 7;
  const approaching = daysRemaining <= 30;

  return (
    <div className={`rounded-lg border p-4 ${
      urgent ? "border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-900/20" :
      approaching ? "border-yellow-300 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20" :
      "border-orange-300 bg-orange-50 dark:border-orange-800 dark:bg-orange-900/20"
    }`}>
      <div className="flex items-start gap-2">
        <span className="text-xl">{urgent ? "🚨" : "⚠️"}</span>
        <div>
          <p className="font-semibold">
            Version {version} is deprecated
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Sunset: {sunsetDate} ({daysRemaining} day{daysRemaining !== 1 ? "s" : ""} remaining)
          </p>
          {replacementVersion && (
            <p className="mt-1 text-sm">
              👉 Upgrade to <span className="font-semibold">v{replacementVersion}</span>
            </p>
          )}
          {migrationGuideUrl && (
            <a href={migrationGuideUrl} className="mt-1 inline-block text-sm text-blue-600 underline" target="_blank" rel="noopener noreferrer">
              Migration Guide →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
