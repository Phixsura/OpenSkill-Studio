"use client";

interface Template { id: string; name: string; icon: string; description: string;
  tech: string[]; files: number; category: string; }
interface TemplateGalleryProps { templates: Template[]; onSelect: (id: string) => void; }

export function TemplateGallery({ templates, onSelect }: TemplateGalleryProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Start with a Template</h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {templates.map(t => (
          <button key={t.id} onClick={() => onSelect(t.id)}
            className="rounded-lg border p-4 text-left hover:border-blue-400 hover:shadow dark:border-gray-700 dark:hover:border-blue-600">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{t.icon}</span>
              <div>
                <p className="font-semibold">{t.name}</p>
                <p className="text-xs text-gray-400">{t.files} files</p>
              </div>
            </div>
            <p className="mt-2 text-xs text-gray-500">{t.description}</p>
            <div className="mt-2 flex gap-1">
              {t.tech.map(tc => (
                <span key={tc} className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] dark:bg-gray-800">{tc}</span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
