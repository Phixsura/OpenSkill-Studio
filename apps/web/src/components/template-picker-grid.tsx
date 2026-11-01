"use client";

interface Template { id: string; name: string; category: string; description: string; }
interface TemplatePickerGridProps { templates: Template[]; onSelect: (id: string) => void; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊" };

export function TemplatePickerGrid({ templates, onSelect }: TemplatePickerGridProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {templates.map(t => (
        <button key={t.id} onClick={() => onSelect(t.id)}
          className="rounded-xl border border-gray-200 p-4 text-left transition hover:border-blue-400 hover:shadow dark:border-gray-700">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{ICONS[t.category] ?? "📦"}</span>
            <h4 className="font-semibold">{t.name}</h4>
          </div>
          <p className="mt-2 text-sm text-gray-500">{t.description}</p>
          <span className="mt-2 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-xs capitalize dark:bg-gray-800">{t.category}</span>
        </button>
      ))}
    </div>
  );
}
