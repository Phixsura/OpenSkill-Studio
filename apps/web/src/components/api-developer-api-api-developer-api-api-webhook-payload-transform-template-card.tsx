"use client";

interface TemplateInfo { template_id: string; name: string; variables: string[]; usage_count: number; }
interface Props { templates: TemplateInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplateCard({ templates, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Transform Templates</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {templates.length} templates</p>
      </div>
      {templates.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No templates</p>
      ) : (
        <div className="space-y-2">
          {templates.map((t) => (
            <div key={t.template_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{t.name}</span>
                <span className="text-gray-400">{t.usage_count} uses</span>
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {t.variables.map((v) => (
                  <span key={v} className="rounded bg-orange-50 px-1 py-0.5 font-mono text-[9px] text-orange-700 dark:bg-orange-900 dark:text-orange-200">{`{{${v}}}`}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
