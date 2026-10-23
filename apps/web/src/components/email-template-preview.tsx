"use client";

import { useState } from "react";

interface Template { id: string; name: string; subject: string; variables: string[]; }
interface EmailTemplatePreviewProps { templates: Template[]; onPreview: (id: string, vars: Record<string, string>) => string;
  onSend: (id: string) => void; }

export function EmailTemplatePreview({ templates, onPreview, onSend }: EmailTemplatePreviewProps) {
  const [selected, setSelected] = useState(templates[0]?.id ?? "");
  const template = templates.find(t => t.id === selected);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Email Templates</h2>
      <div className="flex gap-2">
        {templates.map(t => (
          <button key={t.id} onClick={() => setSelected(t.id)}
            className={`rounded px-3 py-1.5 text-sm ${selected === t.id ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
            {t.name}
          </button>
        ))}
      </div>
      {template && (
        <div className="rounded-lg border p-4 dark:border-gray-700">
          <p className="text-sm font-medium">Subject: {template.subject}</p>
          <div className="mt-2 flex flex-wrap gap-1">
            {template.variables.map(v => (
              <span key={v} className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">
                {`{{${v}}}`}
              </span>
            ))}
          </div>
          <button onClick={() => onSend(template.id)}
            className="mt-3 rounded bg-green-600 px-3 py-1.5 text-sm text-white">
            Send Test Email
          </button>
        </div>
      )}
    </div>
  );
}
