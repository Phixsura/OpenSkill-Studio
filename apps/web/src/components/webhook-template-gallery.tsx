"use client";

interface WebhookTemplate {
  templateId: string; provider: string; name: string;
  description: string; icon: string; events: string[];
}

export function WebhookTemplateGallery({ templates, onUse }: {
  templates: WebhookTemplate[]; onUse?: (templateId: string) => void;
}) {
  const providers = [...new Set(templates.map((t) => t.provider))].sort();

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔗 Webhook Templates</h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {templates.map((t) => (
          <div key={t.templateId} className="rounded-xl border dark:border-gray-700 p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{t.icon}</span>
              <div>
                <span className="font-semibold text-sm">{t.name}</span>
                <span className="text-xs text-gray-400 block">{t.provider}</span>
              </div>
            </div>
            <p className="text-xs text-gray-500 mb-2">{t.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex gap-1">
                {t.events.slice(0, 3).map((e) => (
                  <span key={e} className="text-[10px] bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{e}</span>
                ))}
              </div>
              <button onClick={() => onUse?.(t.templateId)}
                className="text-xs bg-blue-600 text-white px-3 py-1 rounded-lg">Use</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
