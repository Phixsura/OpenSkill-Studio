"use client";
import { useState } from "react";

interface WebhookTemplate { templateId: string; name: string; eventType: string; payloadSchema: Record<string, string>; description: string; }

export function WebhookTemplateBrowser({ templates }: { templates: WebhookTemplate[] }) {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const filtered = templates.filter(t => t.name.toLowerCase().includes(search.toLowerCase()) || t.eventType.toLowerCase().includes(search.toLowerCase()));
  const active = templates.find(t => t.templateId === selected);

  return (
    <div className="space-y-3">
      <input type="text" placeholder="Search templates..." value={search} onChange={e => setSearch(e.target.value)}
        className="w-full border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent" />
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {filtered.map(t => (
          <button key={t.templateId} onClick={() => setSelected(t.templateId)}
            className={`text-left border rounded-xl p-3 text-sm ${selected === t.templateId ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-200 dark:border-gray-700"}`}>
            <span className="font-medium block">{t.name}</span>
            <span className="text-xs text-gray-500 font-mono">{t.eventType}</span>
          </button>
        ))}
      </div>
      {active && (
        <div className="border dark:border-gray-700 rounded-xl p-4 bg-gray-50 dark:bg-gray-800">
          <span className="text-xs font-semibold block mb-2">Payload Schema</span>
          <pre className="text-xs font-mono">{JSON.stringify(active.payloadSchema, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
