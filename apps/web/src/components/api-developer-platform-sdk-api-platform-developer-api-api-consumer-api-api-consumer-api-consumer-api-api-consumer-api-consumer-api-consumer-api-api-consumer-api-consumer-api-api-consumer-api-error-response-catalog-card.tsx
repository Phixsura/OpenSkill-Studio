"use client";

interface ErrorDef { code: string; status: number; title: string; category: string; resolution: string; }
interface Props { errors: ErrorDef[]; appName: string; }

const catColors: Record<string, string> = {
  auth: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  validation: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  rate_limit: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  billing: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  internal: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalogCard({ errors, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 Error Catalog</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {errors.length} error codes</p>
      </div>
      {errors.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error codes registered</p>
      ) : (
        <div className="space-y-2">
          {errors.slice(0, 8).map((e) => (
            <div key={e.code} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1">
                  <code className="font-bold text-gray-700 dark:text-gray-300">{e.code}</code>
                  <span className={`rounded px-1 py-0.5 text-[9px] ${catColors[e.category] ?? "bg-gray-200 text-gray-600"}`}>{e.category}</span>
                </div>
                <span className="font-mono text-[10px] text-gray-400">{e.status}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-500">{e.title}</div>
              {e.resolution && <div className="mt-0.5 text-[9px] text-blue-500">💡 {e.resolution}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
