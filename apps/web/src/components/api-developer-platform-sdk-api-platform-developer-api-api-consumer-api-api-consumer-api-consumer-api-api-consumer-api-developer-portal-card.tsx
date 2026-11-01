"use client";

interface Page { id: string; title: string; slug: string; published: boolean; }
interface Props { title: string; primaryColor: string; pages: Page[]; features: { changelog: boolean; status: boolean; playground: boolean; sdk: boolean }; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiDeveloperPortalCard({ title, primaryColor, pages, features, appName }: Props) {
  const featureList = [features.changelog && "Changelog", features.status && "Status", features.playground && "Playground", features.sdk && "SDKs"].filter(Boolean);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center gap-2">
        <div className="h-4 w-4 rounded" style={{ backgroundColor: primaryColor }} />
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 Developer Portal</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{title}</p>
        </div>
      </div>
      <div className="mb-2 flex flex-wrap gap-1">
        {featureList.map((f) => <span key={String(f)} className="rounded bg-blue-100 px-1.5 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{String(f)}</span>)}
      </div>
      {pages.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No pages</p>
      ) : (
        <div className="space-y-0.5">
          {pages.map((p) => (
            <div key={p.id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.title}</span>
              <span className={p.published ? "text-green-500" : "text-gray-400"}>{p.published ? "Live" : "Draft"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
