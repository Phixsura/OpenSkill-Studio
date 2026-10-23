"use client";

interface Entry { title: string; type: string; date: string; icon: string; }
interface Section { service: string; entries: Entry[]; count: number; }
interface PlatformChangelogPageProps { sections: Section[]; totalEntries: number;
  serviceCount: number; period: string; }

export function PlatformChangelogPage({ sections, totalEntries, serviceCount, period }: PlatformChangelogPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">📝 Platform Changelog</h2>
        <span className="text-xs text-gray-400">{totalEntries} changes · {serviceCount} services · {period}</span>
      </div>
      {sections.map(s => (
        <div key={s.service} className="rounded-xl border p-4 dark:border-gray-700">
          <h3 className="text-sm font-bold mb-2">{s.service} ({s.count})</h3>
          <ul className="space-y-1">
            {s.entries.map((e, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="text-xs mt-0.5">{e.icon}</span>
                <span>{e.title}</span>
                <span className="ml-auto text-xs text-gray-400">{e.date}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
