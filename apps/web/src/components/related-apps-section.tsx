"use client";

interface App { id: string; name?: string; }
interface Section { key: string; title: string; apps: App[]; count: number; }
interface RelatedAppsSectionProps { sections: Section[]; }

export function RelatedAppsSection({ sections }: RelatedAppsSectionProps) {
  const nonEmpty = sections.filter(s => s.count > 0);
  if (nonEmpty.length === 0) return null;
  return (
    <div className="space-y-6">
      {nonEmpty.map(s => (
        <div key={s.key}>
          <h3 className="text-lg font-semibold">{s.title}</h3>
          <div className="mt-2 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {s.apps.map(a => (
              <div key={a.id} className="rounded-lg border border-gray-200 p-3 text-sm dark:border-gray-700">
                <p className="font-medium">{a.name || a.id}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
