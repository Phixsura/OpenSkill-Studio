"use client";

interface ApiVersionBannerProps { version: string; latest: boolean;
  deprecated: boolean; warning: string | null; }

export function ApiVersionBanner({ version, latest, deprecated, warning }: ApiVersionBannerProps) {
  if (latest && !deprecated) return null;
  return (
    <div className={`rounded-lg px-4 py-2 text-sm ${
      deprecated ? "bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800" :
      "bg-blue-50 dark:bg-blue-900/20 text-blue-700"
    }`}>
      {deprecated && <span className="font-medium">⚠️ Deprecated: </span>}
      {warning || `You're using API ${version}. Latest is available.`}
    </div>
  );
}
