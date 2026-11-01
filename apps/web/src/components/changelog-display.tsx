"use client";

interface ChangelogSection { title: string; items: string[]; }
interface ChangelogDisplayProps { version: string; date: string; sections: ChangelogSection[]; breakingChanges?: string[]; }

export function ChangelogDisplay({ version, date, sections, breakingChanges }: ChangelogDisplayProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-baseline gap-2">
        <h2 className="text-xl font-bold">v{version}</h2>
        <span className="text-sm text-gray-400">{date}</span>
      </div>
      {breakingChanges && breakingChanges.length > 0 && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-800 dark:bg-red-900/10">
          <h3 className="text-sm font-semibold text-red-700 dark:text-red-400">⚠️ Breaking Changes</h3>
          <ul className="mt-1 list-inside list-disc text-sm text-red-600 dark:text-red-300">
            {breakingChanges.map((b, i) => <li key={i}>{b}</li>)}
          </ul>
        </div>
      )}
      {sections.map(s => (
        <div key={s.title}>
          <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-300">{s.title}</h3>
          <ul className="mt-1 list-inside list-disc text-sm text-gray-500 dark:text-gray-400">
            {s.items.map((item, i) => <li key={i}>{item}</li>)}
          </ul>
        </div>
      ))}
    </div>
  );
}
