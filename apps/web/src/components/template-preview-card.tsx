"use client";

interface TemplateInfo {
  template_id: string;
  content_type: string;
  variable_count: number;
  preview: string;
}

interface TemplatePreviewCardProps {
  templates: TemplateInfo[];
  appName: string;
}

const TYPE_BADGES: Record<string, string> = {
  "text/html": "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  "text/plain": "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  "application/json": "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
};

export default function TemplatePreviewCard({ templates, appName }: TemplatePreviewCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Templates</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{templates.length} templates</span>
      </div>

      {templates.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No templates registered</p>
      ) : (
        <div className="space-y-2.5">
          {templates.map((t) => (
            <div
              key={t.template_id}
              className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                    {t.template_id}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${TYPE_BADGES[t.content_type] ?? TYPE_BADGES["text/plain"]}`}
                  >
                    {t.content_type}
                  </span>
                </div>
                <span className="text-[11px] text-gray-400">{t.variable_count} variables</span>
              </div>
              <pre className="mt-1.5 overflow-hidden truncate rounded bg-gray-50 px-2 py-1 font-mono text-[11px] text-gray-500 dark:bg-gray-800/50 dark:text-gray-400">
                {t.preview}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
