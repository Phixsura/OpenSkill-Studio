"use client";

interface Template { statusCode: number; errorCode: string; title: string; docsUrl: string; hasOverride: boolean; }
interface Props { templates: Template[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorPageCard({ templates, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">❌ Error Pages</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {templates.length} templates</p>
      </div>
      {templates.length === 0 ? (
        <p className="text-center text-sm text-gray-400">Using default errors</p>
      ) : (
        <div className="space-y-1">
          {templates.map((t) => (
            <div key={t.statusCode} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <div className="flex items-center gap-2">
                <span className={`font-bold ${t.statusCode >= 500 ? "text-red-600" : "text-amber-600"}`}>{t.statusCode}</span>
                <span className="text-gray-700 dark:text-gray-300">{t.title}</span>
                {t.hasOverride && <span className="text-[9px] text-blue-400">custom</span>}
              </div>
              <code className="text-[10px] text-gray-400">{t.errorCode}</code>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
