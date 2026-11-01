"use client";

interface Template { id: string; name: string; contentType: string; variableCount: number; }
interface Props { templates: Template[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookTemplateCard({ templates, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Webhook Templates</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {templates.length} templates</p>
      </div>
      {templates.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No templates</p>
      ) : (
        <div className="space-y-1">
          {templates.map((t) => (
            <div key={t.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <span className="font-medium text-gray-700 dark:text-gray-300">{t.name}</span>
              <div className="flex gap-2 text-[10px] text-gray-400">
                <span>{t.contentType}</span>
                <span>{t.variableCount} vars</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
