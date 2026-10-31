"use client";

interface CauseCount { cause: string; count: number; }
interface Props { causes: CauseCount[]; totalErrors: number; appName: string; }

const causeEmoji: Record<string, string> = { client_error: "🔸", auth_failure: "🔒", rate_limited: "⏱️", server_error: "🔴", timeout: "⌛", validation: "❌", not_found: "🔍" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestErrorClassifierCard({ causes, totalErrors, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Error Classifier</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-red-600 dark:text-red-400">{totalErrors.toLocaleString()}</span>
      </div>
      {causes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No errors</p>
      ) : (
        <div className="space-y-1">
          {causes.map((c) => (
            <div key={c.cause} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{causeEmoji[c.cause] ?? "•"} {c.cause}</span>
              <span className="text-gray-400">{c.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
