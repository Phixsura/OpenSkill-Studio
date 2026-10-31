"use client";

interface AuditResult { webhookId: string; score: number; issues: string[]; compliant: boolean; }
interface Props { audits: AuditResult[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookSecurityCard({ audits, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ Webhook Security</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {audits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No security audits</p>
      ) : (
        <div className="space-y-2">
          {audits.map((a) => (
            <div key={a.webhookId} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{a.webhookId}</code>
                <span className={`font-bold ${a.score >= 80 ? "text-green-600" : a.score >= 50 ? "text-amber-600" : "text-red-600"}`}>{a.score}/100</span>
              </div>
              {a.issues.length > 0 && (
                <div className="mt-1 text-[10px] text-red-400">{a.issues.join(" · ")}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
