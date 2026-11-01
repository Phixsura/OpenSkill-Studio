"use client";

interface TemplateInfo { template_id: string; name: string; method: string; path: string; category: string; usage_count: number; }
interface Props { templates: TemplateInfo[]; categories: string[]; appName: string; }

const methodColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiPlaygroundTemplateCard({ templates, categories, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Playground Templates</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {templates.length} templates · {categories.length} categories</p>
      </div>
      {templates.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No templates</p>
      ) : (
        <div className="space-y-1">
          {templates.map((t) => (
            <div key={t.template_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-medium ${methodColor[t.method] ?? "text-gray-600"}`}>{t.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{t.name}</span>
              </div>
              <span className="text-gray-400">{t.usage_count}× used</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
