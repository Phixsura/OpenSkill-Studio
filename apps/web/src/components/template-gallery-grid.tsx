"use client";

interface Template { id: string; name: string; category: string; description: string; difficulty: string; stars: number; }
interface TemplateGalleryGridProps { templates: Template[]; onSelect: (id: string) => void; }

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: "bg-green-100 text-green-700", intermediate: "bg-yellow-100 text-yellow-700",
  advanced: "bg-red-100 text-red-700",
};

export function TemplateGalleryGrid({ templates, onSelect }: TemplateGalleryGridProps) {
  if (templates.length === 0) return <p className="text-sm text-gray-400">No templates found.</p>;
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {templates.map(t => (
        <button key={t.id} onClick={() => onSelect(t.id)}
          className="rounded-lg border border-gray-200 p-4 text-left transition hover:shadow-md dark:border-gray-700">
          <div className="flex items-start justify-between">
            <h3 className="font-semibold">{t.name}</h3>
            <span className="text-xs text-gray-400">⭐ {t.stars}</span>
          </div>
          <p className="mt-1 text-sm text-gray-500 line-clamp-2">{t.description}</p>
          <div className="mt-2 flex gap-2">
            <span className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700">{t.category}</span>
            <span className={`rounded px-2 py-0.5 text-xs ${DIFFICULTY_COLORS[t.difficulty] || ""}`}>{t.difficulty}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
