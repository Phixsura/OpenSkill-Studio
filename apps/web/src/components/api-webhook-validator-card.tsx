"use client";

interface ValidationIssueInfo { field: string; message: string; }

interface APIWebhookValidatorCardProps { issues: ValidationIssueInfo[]; url: string; appName: string; }

export default function APIWebhookValidatorCard({ issues, url, appName }: APIWebhookValidatorCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Webhook Validator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[11px] font-medium ${issues.length === 0 ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"}`}>
          {issues.length === 0 ? "Valid" : `${issues.length} issues`}
        </span>
      </div>
      {url && <p className="mb-2 truncate text-[10px] text-gray-400">{url}</p>}
      {issues.length > 0 && (
        <div className="space-y-1">
          {issues.map((i, idx) => (
            <p key={idx} className="text-xs text-red-600 dark:text-red-400">⚠ {i.field}: {i.message}</p>
          ))}
        </div>
      )}
    </div>
  );
}
