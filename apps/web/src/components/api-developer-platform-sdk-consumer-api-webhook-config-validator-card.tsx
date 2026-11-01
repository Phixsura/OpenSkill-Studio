"use client";

interface Issue { field: string; severity: string; message: string; }
interface Props { webhookId: string; valid: boolean; score: number; issues: Issue[]; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiWebhookConfigValidatorCard({ webhookId, valid, score, issues, appName }: Props) {
  const errors = issues.filter(i => i.severity === "error");
  const warnings = issues.filter(i => i.severity === "warning");
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Config Validator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {webhookId}</p>
        </div>
        <div className="text-right">
          <div className={`text-lg font-bold ${score >= 80 ? "text-green-600" : score >= 50 ? "text-amber-600" : "text-red-600"}`}>{score}/100</div>
          <div className={`text-[10px] ${valid ? "text-green-500" : "text-red-500"}`}>{valid ? "✅ Valid" : "❌ Invalid"}</div>
        </div>
      </div>
      {issues.length === 0 ? (
        <p className="text-center text-sm text-green-500">All checks passed!</p>
      ) : (
        <div className="space-y-1">
          {errors.map((i, idx) => (
            <div key={idx} className="rounded bg-red-50 px-2 py-1 text-[10px] text-red-700 dark:bg-red-900/20 dark:text-red-400">❌ {i.field}: {i.message}</div>
          ))}
          {warnings.map((i, idx) => (
            <div key={idx} className="rounded bg-amber-50 px-2 py-1 text-[10px] text-amber-700 dark:bg-amber-900/20 dark:text-amber-400">⚠️ {i.field}: {i.message}</div>
          ))}
        </div>
      )}
    </div>
  );
}
