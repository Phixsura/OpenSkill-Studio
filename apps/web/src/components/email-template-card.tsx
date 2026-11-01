"use client";

interface EmailTemplateInfo {
  template_id: string;
  name: string;
  subject: string;
  variable_count: number;
  has_plain_text: boolean;
}

interface EmailTemplateCardProps {
  templates: EmailTemplateInfo[];
  appName: string;
}

export default function EmailTemplateCard({ templates, appName }: EmailTemplateCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Email Templates
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{templates.length} templates</span>
      </div>

      {templates.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No email templates</p>
      ) : (
        <div className="space-y-2">
          {templates.map((t) => (
            <div
              key={t.template_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {t.name}
                </span>
                <span className="font-mono text-[10px] text-gray-400">{t.template_id}</span>
              </div>
              <p className="mt-0.5 text-xs text-gray-500">{t.subject}</p>
              <div className="mt-1 flex items-center gap-2 text-[10px]">
                <span className="rounded bg-blue-100 px-1.5 py-0.5 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                  {t.variable_count} vars
                </span>
                {t.has_plain_text && (
                  <span className="rounded bg-green-100 px-1.5 py-0.5 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                    + plain text
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
