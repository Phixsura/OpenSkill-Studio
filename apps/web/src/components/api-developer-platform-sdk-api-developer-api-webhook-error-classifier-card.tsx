"use client";

interface ErrorInfo { error_class: string; count: number; destinations_count: number; }
interface Props { errors: ErrorInfo[]; totalErrors: number; appName: string; }

const eIcon: Record<string, string> = { timeout: "⏱️", connection_refused: "🚫", dns_failure: "🌐", tls_error: "🔒", http_4xx: "4️⃣", http_5xx: "5️⃣", payload_rejected: "📦" };

export default function APIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifierCard({ errors, totalErrors, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ Error Classifier</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-red-500">{totalErrors.toLocaleString()}</span>
      </div>
      {errors.length === 0 ? (
        <p className="text-center text-sm text-green-600">✓ No webhook errors</p>
      ) : (
        <div className="space-y-1.5">
          {errors.map((e) => (
            <div key={e.error_class} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{eIcon[e.error_class] ?? "•"} {e.error_class}</span>
              <span className="text-gray-400">{e.count}× · {e.destinations_count} dest</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
